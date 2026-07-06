# OLA 360 Prompt And Command Pack

Use this file as the project handoff prompt. It contains the copy-paste commands and operating prompts needed to run, test, sync, and deploy the main OLA 360 app.

## Fresh Computer Full Setup Prompt

Use this when starting from a new Windows computer.

```text
Goal: run OLA 360 from zero on a new Windows computer using VS Code.

Required tools:
- Windows 10 or Windows 11
- Python 3.13.x
- VS Code
- Git, or download ZIP from GitHub if Git is not installed

Repository:
https://github.com/ahmedlabib33-boop/Eng-ola-control-center

Main app folder:
D:\Eng. OLA

Framework:
Flet ASGI app with Python.

Main entrypoint:
main.py

ASGI object:
main:app

Local web port:
6194
```

## New Computer Folder Setup Prompt

Option A - using Git:

```powershell
mkdir D:\Eng. OLA
cd D:\Eng. OLA
git clone https://github.com/ahmedlabib33-boop/Eng-ola-control-center.git .
```

Option B - using GitHub ZIP:

```text
1. Open https://github.com/ahmedlabib33-boop/Eng-ola-control-center
2. Click Code
3. Click Download ZIP
4. Extract the ZIP contents into D:\Eng. OLA
5. Make sure main.py is directly inside D:\Eng. OLA
```

## VS Code Open Project Prompt

```powershell
cd "D:\Eng. OLA"
code .
```

If `code` is not recognized:

```text
Open VS Code manually.
Click File > Open Folder.
Select D:\Eng. OLA.
```

## VS Code Terminal Prompt

Inside VS Code:

```text
Terminal > New Terminal
```

Then run:

```powershell
cd "D:\Eng. OLA"
```

## Create Virtual Environment Prompt

Run once on a fresh computer:

```powershell
cd "D:\Eng. OLA"
py -3.13 -m venv .venv
```

If `py -3.13` does not work:

```powershell
cd "D:\Eng. OLA"
python -m venv .venv
```

## Activate Virtual Environment Prompt

```powershell
cd "D:\Eng. OLA"
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
cd "D:\Eng. OLA"
.\.venv\Scripts\Activate.ps1
```

## Install Dependencies Prompt

```powershell
cd "D:\Eng. OLA"
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## VS Code Select Python Interpreter Prompt

```text
1. Press Ctrl + Shift + P
2. Type: Python: Select Interpreter
3. Choose:
   D:\Eng. OLA\.venv\Scripts\python.exe
```

## Project Identity Prompt

```text
You are working on OLA 360, a mobile-first Flet application for Eng. Ola, Director of the Project Management Office at SAMCO.

Application name: OLA 360
Subtitle: Executive PMO Chief of Staff
Tagline: Executive clarity. Every morning.

The app must remain a premium executive command center, not a generic dashboard. It must support:
- Executive Morning Brief
- Early-Warning and Intervention Radar
- Meetings, Decisions, and Commitments
- AI Executive Chief of Staff with safe fallback
- My Day - Private with data isolation
- More menu pages for reports, decisions, commitments, notifications, templates, intervention, timeline, privacy, settings, and help

Login is currently disabled for the working build. The app opens directly as Eng. Ola.

Do not move current app files into OLD PROGRAM. The main app is in D:\Eng. OLA.
Do not expose secrets or tokens.
Do not include local databases, logs, uploads, exports, .venv, or OLD PROGRAM in public deployment uploads.
```

## Workspace Prompt

```powershell
cd "D:\Eng. OLA"
```

## Quick Run From VS Code Prompt

Best simple command:

```powershell
cd "D:\Eng. OLA"
.\run.bat
```

Choose:

```text
1 = Web app
2 = Desktop app
```

## Quick Web Run Prompt

```powershell
cd "D:\Eng. OLA"
.\run_web.bat
```

Then open:

```text
http://127.0.0.1:6194
```

## Quick Desktop Run Prompt

```powershell
cd "D:\Eng. OLA"
.\run_desktop.bat
```

## Install And Run Prompt

```powershell
cd "D:\Eng. OLA"
.\INSTALL_AND_RUN.ps1
```

## Run Main App Prompt

```powershell
cd "D:\Eng. OLA"
.\RUN_APP.bat
```

Local URL:

```text
http://127.0.0.1:6194
```

## Launcher Menu Prompt

```powershell
cd "D:\Eng. OLA"
.\run.bat
```

Choose:

```text
1 = Web app
2 = Desktop app
```

## Run Flet Web Prompt

```powershell
cd "D:\Eng. OLA"
.\run_web.bat
```

Alternative:

```powershell
cd "D:\Eng. OLA"
.\RUN_FLET_WEB.ps1
```

## Manual Flet Web Run Prompt

Use this if batch files are blocked.

```powershell
cd "D:\Eng. OLA"
.\.venv\Scripts\python.exe -c "from flet.cli import main; main()" run main.py --web --port 6194
```

Open:

```text
http://127.0.0.1:6194
```

## Run Flet Desktop Prompt

```powershell
cd "D:\Eng. OLA"
.\run_desktop.bat
```

Alternative:

```powershell
cd "D:\Eng. OLA"
.\RUN_FLET_DESKTOP.ps1
```

## Manual Flet Desktop Run Prompt

Use this if batch files are blocked.

```powershell
cd "D:\Eng. OLA"
.\.venv\Scripts\python.exe -c "from flet.cli import main; main()" run main.py
```

## Manual ASGI Import Test Prompt

Use this before deployment.

```powershell
cd "D:\Eng. OLA"
.\.venv\Scripts\python.exe -B -c "import main; print(type(main.app).__name__, bool(main.app))"
```

Expected:

```text
FastAPI True
```

## Manual Syntax Test Prompt

```powershell
cd "D:\Eng. OLA"
.\.venv\Scripts\python.exe -B -c "import pathlib; files=list(pathlib.Path('ola_360').rglob('*.py'))+[pathlib.Path('main.py')]+list(pathlib.Path('tests').rglob('*.py')); [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print(f'syntax ok: {len(files)} files')"
```

Expected:

```text
syntax ok: 39 files
```

## Run Tests Prompt

```powershell
cd "D:\Eng. OLA"
.\RUN_TESTS.ps1
```

## Manual Tests Prompt

```powershell
cd "D:\Eng. OLA"
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider --basetemp "$env:TEMP\ola_360_pytest_$PID"
```

Expected:

```text
23 passed
```

## Full Validation Prompt

```powershell
cd "D:\Eng. OLA"
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider --basetemp "$env:TEMP\ola_360_pytest_$PID"
.\.venv\Scripts\python.exe -B -c "import pathlib; files=list(pathlib.Path('ola_360').rglob('*.py'))+[pathlib.Path('main.py')]+list(pathlib.Path('tests').rglob('*.py')); [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print(f'syntax ok: {len(files)} files')"
.\.venv\Scripts\python.exe -B -c "import main; print(type(main.app).__name__, bool(main.app))"
```

Expected results:

```text
23 passed
syntax ok: 39 files
FastAPI True
```

## Restart Local Web App Prompt

```powershell
cd "D:\Eng. OLA"
$listenerIds = netstat -ano | Select-String ':6194' | ForEach-Object { ($_ -split '\s+')[-1] } | Where-Object { $_ -match '^\d+$' -and $_ -ne '0' } | Select-Object -Unique
foreach ($procId in $listenerIds) { try { Stop-Process -Id ([int]$procId) -Force -ErrorAction Stop } catch {} }
Start-Sleep -Seconds 2
Start-Process -FilePath 'D:\Eng. OLA\.venv\Scripts\python.exe' -ArgumentList '-c "from flet.cli import main; main()" run main.py --web --port 6194' -WorkingDirectory 'D:\Eng. OLA' -RedirectStandardOutput 'D:\Eng. OLA\logs\flet_start_stdout.log' -RedirectStandardError 'D:\Eng. OLA\logs\flet_start_stderr.log' -WindowStyle Hidden
Start-Sleep -Seconds 8
Invoke-WebRequest -Uri http://127.0.0.1:6194 -UseBasicParsing | Select-Object StatusCode,StatusDescription
```

Expected result:

```text
StatusCode StatusDescription
---------- -----------------
       200 OK
```

## Stop Local App Prompt

```powershell
$listenerIds = netstat -ano | Select-String ':6194' | ForEach-Object { ($_ -split '\s+')[-1] } | Where-Object { $_ -match '^\d+$' -and $_ -ne '0' } | Select-Object -Unique
foreach ($procId in $listenerIds) { try { Stop-Process -Id ([int]$procId) -Force -ErrorAction Stop } catch {} }
```

## Check Port 6194 Prompt

```powershell
netstat -ano | Select-String ':6194'
```

## Check App In Browser Prompt

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:6194 -UseBasicParsing | Select-Object StatusCode,StatusDescription
```

Expected:

```text
200 OK
```

## Sync GitHub Repo Prompt

Target repo:

```text
https://github.com/ahmedlabib33-boop/Eng-ola-control-center
```

Run:

```powershell
cd "D:\Eng. OLA"
.\sync.bat
```

The sync script reads GitHub token values from `C:\Users\pc\.codex\.env` and must not print tokens.

## Sync From A New Computer Prompt

If the new computer does not have the GitHub token file, use normal Git commands after signing in to GitHub:

```powershell
cd "D:\Eng. OLA"
git status
git add .
git commit -m "Update OLA 360"
git push origin main
```

If Git is not installed, use GitHub Desktop or upload files through GitHub web.

Do not upload:

```text
.venv
data/*.db
logs
uploads
exports
OLD PROGRAM
.env
.env.local
```

## Render Deployment Prompt

Use only if Render does not require a credit card.

```text
Service type: Web Service
Runtime: Python
Branch: main
Build command: pip install -r requirements.txt
Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
ASGI entrypoint: main:app
Instance type: Free
Environment variables: none required for current SQLite fallback build
```

Files:

```text
render.yaml
Procfile
.python-version
docs/RENDER_DEPLOYMENT.md
```

## No-Card Free Deployment Prompt

Use Hugging Face Spaces Docker CPU Basic when Render asks for a credit card.

Manual browser steps:

```text
1. Open https://huggingface.co/new-space
2. Log in.
3. Create a new Space.
4. Select SDK: Docker.
5. Select Hardware: CPU Basic.
6. App port is 7860.
7. Push or upload this repo content.
```

Script deployment:

```powershell
cd "D:\Eng. OLA"
$env:HF_TOKEN="hf_your_token_here"
.\DEPLOY_HUGGINGFACE_SPACE.ps1 -SpaceId "YOUR_HF_USERNAME/ola-360"
```

Expected hosted URL:

```text
https://huggingface.co/spaces/YOUR_HF_USERNAME/ola-360
```

## Hugging Face From New Computer Prompt

```powershell
cd "D:\Eng. OLA"
.\.venv\Scripts\python.exe -m pip install --upgrade huggingface_hub
$env:HF_TOKEN="hf_your_token_here"
.\DEPLOY_HUGGINGFACE_SPACE.ps1 -SpaceId "YOUR_HF_USERNAME/ola-360"
```

If the PowerShell script is blocked:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
cd "D:\Eng. OLA"
.\DEPLOY_HUGGINGFACE_SPACE.ps1 -SpaceId "YOUR_HF_USERNAME/ola-360"
```

## Hugging Face Runtime Prompt

The Docker container starts with:

```bash
uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}
```

Files:

```text
Dockerfile
.dockerignore
DEPLOY_HUGGINGFACE_SPACE.ps1
docs/HUGGINGFACE_SPACES_DEPLOYMENT.md
```

## Streamlit Cloud Prompt

Streamlit Cloud is not the full app host. It only shows a compatibility notice because the app is Flet ASGI.

If Streamlit Cloud opens:

```text
This repository is a Flet application. Streamlit Community Cloud can run the compatibility page, but the full mobile command-center UI should be deployed as an ASGI app or Docker app.
```

## Common Problem Fix Prompts

### Python Not Found

```text
Install Python 3.13 from python.org.
During installation, enable "Add Python to PATH".
Restart VS Code.
```

Then check:

```powershell
python --version
py --version
```

### Flet Command Not Found

Use the Python module launcher:

```powershell
cd "D:\Eng. OLA"
.\.venv\Scripts\python.exe -c "from flet.cli import main; main()" run main.py --web --port 6194
```

### Port Already Used

```powershell
$listenerIds = netstat -ano | Select-String ':6194' | ForEach-Object { ($_ -split '\s+')[-1] } | Where-Object { $_ -match '^\d+$' -and $_ -ne '0' } | Select-Object -Unique
foreach ($procId in $listenerIds) { try { Stop-Process -Id ([int]$procId) -Force -ErrorAction Stop } catch {} }
```

Then run again:

```powershell
cd "D:\Eng. OLA"
.\run_web.bat
```

### PowerShell Script Blocked

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then rerun the script.

### Missing Packages

```powershell
cd "D:\Eng. OLA"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### App Opens Streamlit Compatibility Page

```text
You are using Streamlit Cloud or streamlit run.
The real app is Flet ASGI.
Run locally with run_web.bat or deploy with Docker/ASGI.
```

### Database Reset Prompt

Use only if you intentionally want a fresh local database.

```powershell
cd "D:\Eng. OLA"
Rename-Item "data\ola_360.db" "ola_360_backup.db" -ErrorAction SilentlyContinue
.\run_web.bat
```

Do not delete user data unless explicitly approved.

## Files To Know Prompt

```text
main.py                              ASGI and local app entrypoint
ola_360/app.py                       Flet app composition
ola_360/views/home_view.py           Morning brief and home
ola_360/views/radar_view.py          Early-warning radar
ola_360/views/meetings_view.py       Meetings and commitments
ola_360/views/ai_view.py             AI Chief of Staff
ola_360/views/my_day_view.py         Private My Day
ola_360/views/secondary_view.py      More menu pages
ola_360/repositories/database.py     SQLite setup
ola_360/repositories/app_repository.py Data access
ola_360/services/ai_service.py       AI fallback
ola_360/services/import_service.py   CSV/XLSX imports
ola_360/services/report_service.py   PMO reports
templates/                           Import templates
docs/                                Documentation
prompt.md                            Full command pack
```

## Meeting Extraction Feature Prompt

```text
Improve the Meeting and Commitment Center.

It must support recording or transcript paste, then extract:
- Discussion summary
- Decision
- Action required
- Responsible person
- Due date
- Priority
- Related project
- Related warning
- Supporting attachment

It must auto-generate reviewable outputs:
- Meeting minutes
- Action register
- Decision register
- Follow-up email draft
- Next meeting agenda
- Overdue-action list

Never save AI-extracted actions without user review and approval.
```

## Feature Improvement Prompt

```text
Improve OLA 360 without changing the main identity or moving files.

Keep the design premium, mature, mobile-first, and suitable for a senior PMO executive.
Add practical features that make daily work easier:
- Executive focus list
- Intervention cockpit
- PMO report generation
- Meeting template center
- Commitment timeline
- End-of-day review
- Tomorrow plan
- Data import validation
- Safe AI fallback
- Private My Day isolation

Run tests and verify main:app before syncing.
```

## Design Prompt

```text
Preserve the OLA 360 premium executive style.

Use:
- Deep plum or aubergine
- Charcoal or midnight graphite
- Warm ivory or light stone
- Muted rose gold or bronze
- Controlled emerald
- Refined amber
- Deep red
- Muted blue

Mobile-first target: 390 x 844.
No horizontal scrolling.
Bottom navigation.
Touch targets at least 44 px.
Clear cards, calm spacing, strong headings, readable body text.
Avoid childish colors, excessive pink, flowers, generic dashboards, tiny text, crowded charts, and fake AI outputs.
```

## AI Guardrail Prompt

```text
The AI Executive Chief of Staff must answer from app data only.

Requirements:
- No invented project facts
- Show missing-data warnings
- Separate fact from inference
- Use source references when available
- Keep drafts editable
- Do not send messages automatically
- Do not modify records without approval
- Keep My Day private data outside organizational AI unless Eng. Ola explicitly opens the private module
- Provide rule-based fallback when AI providers are unavailable
```

## Private Module Prompt

```text
My Day - Private must remain isolated from corporate PMO data.

Private data must:
- Use separate database tables
- Never appear in PMO reports
- Never appear in organizational AI responses
- Never be visible to normal administrators
- Never be included in corporate exports
- Never be used for project analytics
```

## Final Delivery Prompt

```text
Before final delivery:
1. Run tests.
2. Run syntax check.
3. Confirm main.app imports as an ASGI object.
4. Confirm local app returns HTTP 200 if a local run was requested.
5. Sync to GitHub if requested.
6. Report the repo URL, commit hash, and exact commands used.
```
