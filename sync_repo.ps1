$ErrorActionPreference = "Stop"

$Owner = "ahmedlabib33-boop"
$Repo = "Eng-ola-control-center"
$Branch = "main"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$EnvFile = "C:\Users\pc\.codex\.env"

if (Test-Path -LiteralPath $EnvFile) {
  Get-Content -LiteralPath $EnvFile | ForEach-Object {
    if ($_ -match "^\s*([^#][^=]+?)\s*=\s*(.+?)\s*$") {
      $name = $matches[1].Trim()
      $value = $matches[2].Trim().Trim('"').Trim("'")
      if (-not [Environment]::GetEnvironmentVariable($name, "Process")) {
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
      }
    }
  }
}

$Token = $env:GITHUB_TOKEN
if (-not $Token) { $Token = $env:GH_TOKEN }
if (-not $Token) {
  throw "Missing GitHub token. Set GITHUB_TOKEN or GH_TOKEN, or save it in C:\Users\pc\.codex\.env."
}

$Headers = @{
  Authorization = "Bearer $Token"
  Accept = "application/vnd.github+json"
  "X-GitHub-Api-Version" = "2022-11-28"
  "User-Agent" = "OLA-360-sync"
}

function Invoke-GitHub {
  param(
    [string]$Method,
    [string]$Uri,
    [object]$Body = $null
  )
  if ($null -eq $Body) {
    return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $Headers
  }
  $json = $Body | ConvertTo-Json -Depth 20
  return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $Headers -Body $json -ContentType "application/json"
}

function Test-ExcludedPath {
  param([string]$RelativePath)
  $normalized = $RelativePath.Replace("\", "/")
  $first = ($normalized -split "/")[0]
  $excludedDirs = @(".git", ".venv", "OLD PROGRAM", "data", "logs", "exports", "uploads", "__pycache__", ".pytest_tmp", ".pytest_cache", ".agents", ".codex")
  if ($excludedDirs -contains $first) { return $true }
  if ($normalized -match "/__pycache__/") { return $true }
  if ($normalized.EndsWith(".pyc")) { return $true }
  if ($normalized.EndsWith(".db")) { return $true }
  if ($normalized.EndsWith(".log")) { return $true }
  return $false
}

Set-Location -LiteralPath $Root

Write-Host "Syncing D:\Eng. OLA to https://github.com/$Owner/$Repo on branch $Branch"

$repoUri = "https://api.github.com/repos/$Owner/$Repo"
$repoInfo = Invoke-GitHub -Method Get -Uri $repoUri
if (-not $repoInfo) { throw "Repository not found or token has no access: $Owner/$Repo" }

try {
  Invoke-GitHub -Method Get -Uri "$repoUri/git/ref/heads/$Branch" | Out-Null
} catch {
  Write-Host "Repository branch $Branch is not initialized. Creating first branch commit."
  $initContent = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("Initialized for OLA 360 sync.`n"))
  try {
    Invoke-GitHub -Method Put -Uri "$repoUri/contents/.repo-initialized" -Body @{
      message = "Initialize $Branch branch"
      content = $initContent
      branch = $Branch
    } | Out-Null
  } catch {
    Invoke-GitHub -Method Put -Uri "$repoUri/contents/.repo-initialized" -Body @{
      message = "Initialize $Branch branch"
      content = $initContent
    } | Out-Null
  }
}

$files = Get-ChildItem -LiteralPath $Root -Recurse -File -Force |
  ForEach-Object {
    $relative = $_.FullName.Substring($Root.Length).TrimStart("\", "/")
    if (-not (Test-ExcludedPath $relative)) {
      [PSCustomObject]@{
        FullName = $_.FullName
        Path = $relative.Replace("\", "/")
      }
    }
  } |
  Sort-Object Path

if (-not $files -or $files.Count -eq 0) {
  throw "No files selected for sync."
}

$treeItems = @()
foreach ($file in $files) {
  $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
  $blob = Invoke-GitHub -Method Post -Uri "$repoUri/git/blobs" -Body @{
    content = [Convert]::ToBase64String($bytes)
    encoding = "base64"
  }
  $treeItems += @{
    path = $file.Path
    mode = "100644"
    type = "blob"
    sha = $blob.sha
  }
  Write-Host "Prepared $($file.Path)"
}

$headSha = $null
$baseTreeSha = $null
try {
  $ref = Invoke-GitHub -Method Get -Uri "$repoUri/git/ref/heads/$Branch"
  $headSha = $ref.object.sha
  $headCommit = Invoke-GitHub -Method Get -Uri "$repoUri/git/commits/$headSha"
  $baseTreeSha = $headCommit.tree.sha
} catch {
  Write-Host "Branch $Branch does not exist yet. Creating initial commit."
}

$treeBody = @{ tree = $treeItems }
if ($baseTreeSha) { $treeBody.base_tree = $baseTreeSha }
$newTree = Invoke-GitHub -Method Post -Uri "$repoUri/git/trees" -Body $treeBody

$message = "Sync OLA 360 app from local workspace"
$commitBody = @{
  message = $message
  tree = $newTree.sha
  parents = @()
}
if ($headSha) { $commitBody.parents = @($headSha) }
$commit = Invoke-GitHub -Method Post -Uri "$repoUri/git/commits" -Body $commitBody

if ($headSha) {
  Invoke-GitHub -Method Patch -Uri "$repoUri/git/refs/heads/$Branch" -Body @{
    sha = $commit.sha
    force = $false
  } | Out-Null
} else {
  Invoke-GitHub -Method Post -Uri "$repoUri/git/refs" -Body @{
    ref = "refs/heads/$Branch"
    sha = $commit.sha
  } | Out-Null
}

Write-Host ""
Write-Host "Sync complete."
Write-Host "Repo: https://github.com/$Owner/$Repo"
Write-Host "Branch: $Branch"
Write-Host "Commit: $($commit.sha)"
