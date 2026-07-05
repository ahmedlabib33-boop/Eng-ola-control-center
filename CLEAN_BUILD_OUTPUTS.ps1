$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $Root
$Targets = @("build", "dist", ".pytest_cache")
foreach ($Target in $Targets) {
  $Path = Join-Path $Root $Target
  if (Test-Path -LiteralPath $Path) {
    $Resolved = (Resolve-Path -LiteralPath $Path).Path
    if ($Resolved.StartsWith($Root, [System.StringComparison]::OrdinalIgnoreCase)) {
      Remove-Item -LiteralPath $Resolved -Recurse -Force
    }
  }
}
Write-Host "Cleaned build outputs. Source folders and data are preserved."
