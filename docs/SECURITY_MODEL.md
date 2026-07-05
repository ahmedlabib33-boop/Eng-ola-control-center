# Security Model

- Passwords use PBKDF2-HMAC-SHA256 with per-password salt.
- No plaintext passwords.
- No API keys in source.
- Private My Day data uses separate private tables and is excluded from organizational AI context by default.
- Audit logs record create/status operations.
- Upload validation allows CSV/XLSX extensions only in the first local version.
- Session timeout configuration is prepared in settings.
