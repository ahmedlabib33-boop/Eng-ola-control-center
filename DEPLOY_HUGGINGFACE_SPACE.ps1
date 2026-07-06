param(
    [Parameter(Mandatory = $true)]
    [string]$SpaceId,

    [string]$Token = $env:HF_TOKEN
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$EnvFile = Join-Path $env:USERPROFILE ".codex\.env"

if (-not $Token -and (Test-Path $EnvFile)) {
    $line = Get-Content $EnvFile | Where-Object { $_ -match '^(HF_TOKEN|HUGGINGFACE_TOKEN)=' } | Select-Object -First 1
    if ($line) {
        $Token = ($line -split '=', 2)[1].Trim()
    }
}

if (-not $Token) {
    Write-Host "HF_TOKEN is required." -ForegroundColor Yellow
    Write-Host "Create a Hugging Face token, then run:" -ForegroundColor Yellow
    Write-Host '$env:HF_TOKEN="hf_xxx"; .\DEPLOY_HUGGINGFACE_SPACE.ps1 -SpaceId "YOUR_HF_USERNAME/ola-360"'
    exit 1
}

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $Python = "python"
}

Write-Host "Installing Hugging Face deployment helper if needed..."
& $Python -m pip install --quiet --upgrade huggingface_hub

$env:HF_TOKEN = $Token
$env:HF_SPACE_ID = $SpaceId
$env:OLA_PROJECT_ROOT = $ProjectRoot

Write-Host "Publishing OLA 360 to Hugging Face Space: $SpaceId"

$DeployPython = @'
import os
from pathlib import Path
from huggingface_hub import HfApi, create_repo

token = os.environ["HF_TOKEN"]
space_id = os.environ["HF_SPACE_ID"]
root = Path(os.environ["OLA_PROJECT_ROOT"])

create_repo(
    repo_id=space_id,
    repo_type="space",
    space_sdk="docker",
    private=False,
    exist_ok=True,
    token=token,
)

api = HfApi(token=token)
api.upload_folder(
    folder_path=str(root),
    repo_id=space_id,
    repo_type="space",
    commit_message="Deploy OLA 360 Flet Docker app",
    ignore_patterns=[
        ".git/*",
        ".venv/*",
        "OLD PROGRAM/*",
        "data/*.db",
        "logs/*",
        "exports/*",
        "uploads/*",
        "__pycache__/*",
        "**/__pycache__/*",
        "*.pyc",
        ".pytest_cache/*",
        ".env",
        ".env.local",
    ],
)

print(f"https://huggingface.co/spaces/{space_id}")
'@

$DeployPython | & $Python -

Write-Host "Deployment upload complete." -ForegroundColor Green
