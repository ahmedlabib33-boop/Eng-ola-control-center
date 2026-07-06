# Known Limitations

- Cloud AI and Ollama are optional and not required for the first local version.
- Push notifications are prepared architecturally but not sent to Android yet.
- Native iOS build requires macOS and Apple signing.
- Excel import is prepared through dependency support; CSV preview is implemented first.
- Light mode is planned through theme tokens; the current visual implementation focuses on Dark Intelligence.
## External Provider Credentials

Real speech-to-text, calendar import, email, Teams, and WhatsApp delivery require provider credentials in environment variables. The app does not hard-code secrets and does not pretend to send or transcribe when credentials are missing.

The app remains usable without these credentials: transcripts can be pasted/imported, notification drafts are logged, and AI/query features continue to work from stored SQLite records.
