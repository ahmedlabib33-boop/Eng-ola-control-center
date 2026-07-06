# Hugging Face Spaces Deployment

Use this when Render asks for a credit card. Hugging Face Spaces can run Docker apps on CPU Basic free hardware.

## Space Settings

- Space SDK: Docker
- Hardware: CPU Basic
- App port: `7860`
- Visibility: Public or Private, as preferred

## Required Files

The repository includes:

- `Dockerfile`
- `.dockerignore`
- README metadata:
  - `sdk: docker`
  - `app_port: 7860`

## Create The Space

1. Open `https://huggingface.co/new-space`.
2. Choose your Hugging Face owner.
3. Name the Space, for example `ola-360`.
4. Select `Docker`.
5. Select free `CPU Basic`.
6. Create the Space.
7. Upload or push this repository content to the Space repository.

## Publish By Script

Create a Hugging Face access token, then run:

```powershell
cd "D:\Eng. OLA"
$env:HF_TOKEN="hf_your_token_here"
.\DEPLOY_HUGGINGFACE_SPACE.ps1 -SpaceId "YOUR_HF_USERNAME/ola-360"
```

The script creates the Docker Space if needed and uploads the app files. It excludes local databases, logs, uploads, exports, virtual environments, and old archived program files.

## Expected Runtime

The Docker container starts:

```bash
uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}
```

## Verify

Open the Space URL and verify:

- The real OLA 360 Flet UI appears.
- The Streamlit compatibility page does not appear.
- Home, Radar, Meetings, AI, My Day, and More pages open.

## Limitations

Free CPU Basic Spaces can sleep after inactivity. The current SQLite database is stored on the Space filesystem and should be treated as non-production persistence unless persistent storage or an external database is configured.
