from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 220_000)
    return f"pbkdf2_sha256${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, salt_hex, digest_hex = encoded.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    expected = hash_password(password, bytes.fromhex(salt_hex)).split("$", 2)[2]
    return hmac.compare_digest(expected, digest_hex)


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


def session_expires(minutes: int) -> str:
    return (datetime.utcnow() + timedelta(minutes=minutes)).isoformat()
