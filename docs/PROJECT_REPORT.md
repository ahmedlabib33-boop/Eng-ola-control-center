# OLA 360 Project And Deployment Report

## Project

OLA 360 is a mobile-first Flet application for Eng. Ola, Director of the Project Management Office at SAMCO.

Application title:

```text
OLA 360 | Executive PMO Chief of Staff
```

Purpose:

```text
Executive clarity. Every morning.
```

The app is a private executive PMO command center covering:

- Executive Morning Brief
- Early-Warning and Intervention Radar
- Meetings, Decisions, and Commitments
- AI Executive Chief of Staff with safe fallback
- My Day - Private
- Reports, templates, intervention cockpit, timeline, notifications, settings, privacy, and help pages

## Current Repository

```text
https://github.com/ahmedlabib33-boop/Eng-ola-control-center
```

Current branch:

```text
main
```

Current local project folder:

```text
D:\Eng. OLA
```

## Current Deployment Status

The project is deployed on Hugging Face Spaces with a permanent secure HTTPS URL.

Current status:

```text
GitHub repo: synced
Render deployment: prepared, not completed because card was required
Hugging Face Spaces deployment: live
Streamlit Cloud: compatibility notice only, not the full app
```

Permanent app URL:

```text
https://ahmedbeba-beba.hf.space/
```

Hugging Face Space page:

```text
https://huggingface.co/spaces/ahmedbeba/beba
```

## Main Deployment Option

Render ASGI deployment is configured with:

```text
Build command:
pip install -r requirements.txt

Start command:
uvicorn main:app --host 0.0.0.0 --port $PORT

ASGI entrypoint:
main:app
```

Render files:

```text
render.yaml
Procfile
.python-version
docs/RENDER_DEPLOYMENT.md
```

## No-Card Free Deployment Option

Use Hugging Face Spaces Docker CPU Basic when Render requires a credit card.

Hugging Face settings:

```text
SDK: Docker
Hardware: CPU Basic
App port: 7860
```

Deployment files:

```text
Dockerfile
.dockerignore
DEPLOY_HUGGINGFACE_SPACE.ps1
docs/HUGGINGFACE_SPACES_DEPLOYMENT.md
```

Hugging Face script:

```powershell
cd "D:\Eng. OLA"
$env:HF_TOKEN="hf_your_token_here"
.\DEPLOY_HUGGINGFACE_SPACE.ps1 -SpaceId "YOUR_HF_USERNAME/ola-360"
```

Public URL:

```text
https://ahmedbeba-beba.hf.space/
```

## Local Run

Only two app launcher batch files are kept:

```text
run_web.bat
run_desktop.bat
```

Run web:

```powershell
cd "D:\Eng. OLA"
.\run_web.bat
```

Open:

```text
http://127.0.0.1:6194
```

Run desktop:

```powershell
cd "D:\Eng. OLA"
.\run_desktop.bat
```

## Meeting Transcript And Summary

The Meeting and Commitment Center supports:

- Real speech-to-text integration for audio files when `OPENAI_API_KEY` is configured
- Verbatim transcript paste
- `.txt` transcript import
- Exact transcript preservation
- Transcript word count
- Discussion summary in bullet points
- Decision extraction
- Action extraction
- Responsible person
- Due date
- Priority
- Related project
- Related warning
- Supporting attachment
- Meeting minutes
- Action register
- Decision register
- Follow-up email draft
- Next meeting agenda
- Overdue-action list

Important limitation:

```text
The current Flet version has no built-in live microphone control.
The app does not claim fake browser microphone recording.
It transcribes audio files with a configured speech-to-text provider, preserves pasted/imported/provider transcript text exactly, and generates reviewed outputs from that transcript.
```

## Added Executive Capabilities

```text
Portfolio-wide risk rollup
Predictive early-warning signals from project update trends
Automatic overdue escalation nudges
Weekly and monthly executive digest generation as Markdown and PDF
Decision audit trail linked to meeting source where available
Email, Teams, and WhatsApp notification delivery with draft fallback
Voice quick capture for private notes using the configured speech-to-text provider
Role/delegate records for Deputy, PMO Analyst, and PMO Admin
Natural-language query over stored warnings, commitments, and decisions
Calendar import from ICS feed through OLA_CALENDAR_ICS_URL
```

## External Integration Configuration

No API keys are hard-coded. External integrations activate only when these environment variables are configured:

```text
OPENAI_API_KEY                 Real speech-to-text transcription
OLA_STT_PROVIDER               Optional, defaults to openai
OLA_STT_MODEL                  Optional, defaults to whisper-1
OLA_CALENDAR_ICS_URL           Outlook/Google/public ICS calendar import
OLA_SMTP_HOST                  Email notifications
OLA_SMTP_PORT                  Email notifications, defaults to 587
OLA_SMTP_USER                  Email login
OLA_SMTP_PASSWORD              Email login
OLA_SMTP_FROM                  Email sender
OLA_TEAMS_WEBHOOK_URL          Teams notifications
TWILIO_ACCOUNT_SID             WhatsApp notifications
TWILIO_AUTH_TOKEN              WhatsApp notifications
TWILIO_WHATSAPP_FROM           WhatsApp sender
```

## Latest Verification

Last local checks completed successfully:

```text
Tests: 27 passed
Syntax: syntax ok: 46 files
ASGI import: FastAPI True
Transcript smoke test: exact transcript preserved = True
Hugging Face Space status: Running
Container: Uvicorn running on http://0.0.0.0:7860
Public URL: https://ahmedbeba-beba.hf.space/
```

## Redeploy Notes

The Hugging Face Space contains a Dockerfile that pulls the current GitHub `main` branch during build:

```text
https://github.com/ahmedlabib33-boop/Eng-ola-control-center
```

When the GitHub repo is updated, restart/rebuild the Hugging Face Space to pull the latest app code.

```text
https://huggingface.co/spaces/YOUR_HF_USERNAME/ola-360
```
