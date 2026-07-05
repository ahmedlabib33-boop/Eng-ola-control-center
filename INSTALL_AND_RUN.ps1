$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $Root

if (!(Get-Command python -ErrorAction SilentlyContinue)) {
  throw "Python is required. Install Python 3.11+ and retry."
}

if (!(Test-Path ".venv\Scripts\python.exe")) {
  python -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".\.venv\Scripts\python.exe" -c "from flet.cli import main; main()" run main.py --web --port 6194
