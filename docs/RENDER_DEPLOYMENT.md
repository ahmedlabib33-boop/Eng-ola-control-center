# Render Deployment

OLA 360 is a Flet ASGI application. Deploy the full mobile command-center UI on Render as a Python Web Service.

Streamlit Community Cloud should remain only as a compatibility notice. It cannot host the full Flet ASGI UI correctly.

## Repository

Use the same GitHub repository:

```text
ahmedlabib33-boop/Eng-ola-control-center
```

## Render Settings

- Service type: Web Service
- Runtime: Python
- Branch: main
- Instance type: Free
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- ASGI entrypoint: `main:app`
- Environment variables: none required for the current SQLite fallback build

The repository also includes `render.yaml`, so Render can create the service from a Blueprint.

## Before Deployment

Run locally:

```powershell
cd "D:\Eng. OLA"
.\RUN_TESTS.ps1
.\.venv\Scripts\python.exe -B -c "import main; print(bool(main.app))"
```

The import check must print:

```text
True
```

## After Deployment

Open the Render public URL and verify:

- The real OLA 360 Flet UI appears.
- The Streamlit compatibility page does not appear.
- No login page appears.
- Home, Radar, Meetings, AI, My Day, and More pages open.
- Reports, templates, intervention, timeline, and end-of-day review pages open.

## Operational Notes

Render's free tier may sleep after inactivity. The first request after sleep can be slower.

The current app uses local SQLite. For persistent production data, migrate storage to a managed database such as Supabase PostgreSQL before relying on Render ephemeral filesystem storage.
