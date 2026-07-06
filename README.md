---
title: OLA 360
sdk: docker
app_port: 7860
pinned: false
---

# OLA 360

**OLA 360 | Executive PMO Chief of Staff** is a mobile-first Flet application for secure morning briefings, early warnings, meetings, commitments, safe AI assistance, and private personal productivity.

## Run Locally

```powershell
cd "D:\Eng. OLA"
.\INSTALL_AND_RUN.ps1
```

Login is currently disabled for the local working build. The app opens directly as Eng. Ola.

Seeded credentials are still preserved for when login is restored:

- Email: `ola@samco.local`
- Password: `Ola360!`

## Run Modes

- Launcher menu: `.\run.bat`
- Web batch: `.\run_web.bat`
- Desktop batch: `.\run_desktop.bat`
- Web: `.\RUN_FLET_WEB.ps1`
- Desktop: `.\RUN_FLET_DESKTOP.ps1`
- Main launcher: `.\RUN_APP.bat`
- Tests: `.\RUN_TESTS.ps1`
- Command and handoff prompts: `prompt.md`

The database is stored at `data/ola_360.db` and is not deleted by build/clean scripts.

## Public Deployment

The full OLA 360 app is a Flet ASGI application. Deploy it on Render as a Python Web Service from:

```text
ahmedlabib33-boop/Eng-ola-control-center
```

Render settings:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- ASGI entrypoint: `main:app`
- Branch: `main`
- Instance type: Free

The repository includes `render.yaml`, `.python-version`, and `Procfile` for deployment. Streamlit Cloud remains only a compatibility notice and is not the main public app host.

Full deployment checklist: `docs/RENDER_DEPLOYMENT.md`.

## No-Card Free Deployment

If Render asks for a credit card, deploy on Hugging Face Spaces using Docker CPU Basic.

- Dockerfile: `Dockerfile`
- App port: `7860`
- Start command inside Docker: `uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}`
- Publish script: `.\DEPLOY_HUGGINGFACE_SPACE.ps1 -SpaceId "YOUR_HF_USERNAME/ola-360"`
- Guide: `docs/HUGGINGFACE_SPACES_DEPLOYMENT.md`

## Data Input Templates

Templates are in `templates/`.

- `warnings_template.csv` and `critical_issues_template.csv` import through Radar.
- `warning_evidence_template.csv` supports evidence rows linked to warnings.
- `meetings_template.csv`, `attendees_template.csv`, and `agenda_items_template.csv` support meeting setup and agenda preparation.
- `commitments_template.csv`, `decisions_template.csv`, and `milestones_template.csv` import through Meetings.
- `personal_tasks_template.csv` imports through My Day - Private.
- `meeting_notes_template.txt` can be pasted into the Meetings recording/transcript box before extraction.

CSV and XLSX files are supported when the headers match the templates. Exports are written to `exports/`. Imported and AI-extracted actions remain reviewable before management use.

Executive PMO reports can be generated from Home. The report is written to `exports/` as Markdown and uses PMO records only; My Day private records are excluded.

## Old Program

The previous Streamlit version and other non-main folders are archived in:

```text
D:\Eng. OLA\OLD PROGRAM
```
