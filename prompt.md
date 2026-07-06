# OLA 360 Prompts

```text
You are working on OLA 360, a mobile-first Flet application for Eng. Ola, Director of the Project Management Office at SAMCO.

Application name: OLA 360
Subtitle: Executive PMO Chief of Staff
Tagline: Executive clarity. Every morning.

Keep the app premium, mature, mobile-first, executive, practical, secure, and calm.
Do not expose secrets or tokens.
Do not upload .venv, data/*.db, logs, uploads, exports, OLD PROGRAM, .env, or .env.local.
Main folder: D:\Eng. OLA
Main entrypoint: main.py
ASGI object: main:app
Local web port: 6194
```

```powershell
mkdir "D:\Eng. OLA"
cd "D:\Eng. OLA"
git clone https://github.com/ahmedlabib33-boop/Eng-ola-control-center.git .
```

```text
Open VS Code.
Click File > Open Folder.
Select D:\Eng. OLA.
Open Terminal > New Terminal.
```

```powershell
cd "D:\Eng. OLA"
code .
```

```powershell
cd "D:\Eng. OLA"
py -3.13 -m venv .venv
```

```powershell
cd "D:\Eng. OLA"
python -m venv .venv
```

```powershell
cd "D:\Eng. OLA"
.\.venv\Scripts\Activate.ps1
```

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
cd "D:\Eng. OLA"
.\.venv\Scripts\Activate.ps1
```

```powershell
cd "D:\Eng. OLA"
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

```text
In VS Code:
Press Ctrl + Shift + P.
Type Python: Select Interpreter.
Choose D:\Eng. OLA\.venv\Scripts\python.exe.
```

```powershell
cd "D:\Eng. OLA"
.\run_web.bat
```

```text
Open http://127.0.0.1:6194
```

```powershell
cd "D:\Eng. OLA"
.\run_desktop.bat
```

```powershell
cd "D:\Eng. OLA"
.\INSTALL_AND_RUN.ps1
```

```powershell
cd "D:\Eng. OLA"
.\RUN_FLET_WEB.ps1
```

```powershell
cd "D:\Eng. OLA"
.\RUN_FLET_DESKTOP.ps1
```

```powershell
cd "D:\Eng. OLA"
.\.venv\Scripts\python.exe -c "from flet.cli import main; main()" run main.py --web --port 6194
```

```powershell
cd "D:\Eng. OLA"
.\.venv\Scripts\python.exe -c "from flet.cli import main; main()" run main.py
```

```powershell
cd "D:\Eng. OLA"
.\RUN_TESTS.ps1
```

```powershell
cd "D:\Eng. OLA"
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider --basetemp "$env:TEMP\ola_360_pytest_$PID"
```

```powershell
cd "D:\Eng. OLA"
.\.venv\Scripts\python.exe -B -c "import pathlib; files=list(pathlib.Path('ola_360').rglob('*.py'))+[pathlib.Path('main.py')]+list(pathlib.Path('tests').rglob('*.py')); [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print(f'syntax ok: {len(files)} files')"
```

```powershell
cd "D:\Eng. OLA"
.\.venv\Scripts\python.exe -B -c "import main; print(type(main.app).__name__, bool(main.app))"
```

```powershell
cd "D:\Eng. OLA"
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider --basetemp "$env:TEMP\ola_360_pytest_$PID"
.\.venv\Scripts\python.exe -B -c "import pathlib; files=list(pathlib.Path('ola_360').rglob('*.py'))+[pathlib.Path('main.py')]+list(pathlib.Path('tests').rglob('*.py')); [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print(f'syntax ok: {len(files)} files')"
.\.venv\Scripts\python.exe -B -c "import main; print(type(main.app).__name__, bool(main.app))"
```

```powershell
cd "D:\Eng. OLA"
$listenerIds = netstat -ano | Select-String ':6194' | ForEach-Object { ($_ -split '\s+')[-1] } | Where-Object { $_ -match '^\d+$' -and $_ -ne '0' } | Select-Object -Unique
foreach ($procId in $listenerIds) { try { Stop-Process -Id ([int]$procId) -Force -ErrorAction Stop } catch {} }
Start-Sleep -Seconds 2
Start-Process -FilePath 'D:\Eng. OLA\.venv\Scripts\python.exe' -ArgumentList '-c "from flet.cli import main; main()" run main.py --web --port 6194' -WorkingDirectory 'D:\Eng. OLA' -RedirectStandardOutput 'D:\Eng. OLA\logs\flet_start_stdout.log' -RedirectStandardError 'D:\Eng. OLA\logs\flet_start_stderr.log' -WindowStyle Hidden
Start-Sleep -Seconds 8
Invoke-WebRequest -Uri http://127.0.0.1:6194 -UseBasicParsing | Select-Object StatusCode,StatusDescription
```

```powershell
$listenerIds = netstat -ano | Select-String ':6194' | ForEach-Object { ($_ -split '\s+')[-1] } | Where-Object { $_ -match '^\d+$' -and $_ -ne '0' } | Select-Object -Unique
foreach ($procId in $listenerIds) { try { Stop-Process -Id ([int]$procId) -Force -ErrorAction Stop } catch {} }
```

```powershell
netstat -ano | Select-String ':6194'
```

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:6194 -UseBasicParsing | Select-Object StatusCode,StatusDescription
```

```powershell
cd "D:\Eng. OLA"
.\sync.bat
```

```powershell
cd "D:\Eng. OLA"
git status
git add .
git commit -m "Update OLA 360"
git push origin main
```

```text
Render deployment:
Service type: Web Service
Runtime: Python
Branch: main
Build command: pip install -r requirements.txt
Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
ASGI entrypoint: main:app
Instance type: Free
Environment variables: none required for current SQLite fallback build
```

```text
Hugging Face Spaces deployment:
Open https://huggingface.co/new-space
Log in.
Create a new Space.
Select SDK: Docker.
Select Hardware: CPU Basic.
Set app port to 7860.
Upload or push this repository content.
```

```powershell
cd "D:\Eng. OLA"
$env:HF_TOKEN="hf_your_token_here"
.\DEPLOY_HUGGINGFACE_SPACE.ps1 -SpaceId "YOUR_HF_USERNAME/ola-360"
```

```powershell
cd "D:\Eng. OLA"
.\.venv\Scripts\python.exe -m pip install --upgrade huggingface_hub
$env:HF_TOKEN="hf_your_token_here"
.\DEPLOY_HUGGINGFACE_SPACE.ps1 -SpaceId "YOUR_HF_USERNAME/ola-360"
```

```bash
uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}
```

```text
If Streamlit Cloud opens, remember this is not the full app host.
The real app is Flet ASGI.
Run locally with run_web.bat or deploy with Docker/ASGI.
```

```text
Install Python 3.13 from python.org.
During installation, enable Add Python to PATH.
Restart VS Code.
```

```powershell
python --version
py --version
```

```powershell
cd "D:\Eng. OLA"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

```powershell
cd "D:\Eng. OLA"
Rename-Item "data\ola_360.db" "ola_360_backup.db" -ErrorAction SilentlyContinue
.\run_web.bat
```

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

```text
Before final delivery:
1. Run tests.
2. Run syntax check.
3. Confirm main.app imports as an ASGI object.
4. Confirm local app returns HTTP 200 if a local run was requested.
5. Sync to GitHub if requested.
6. Report the repo URL, commit hash, and exact commands used.
```
