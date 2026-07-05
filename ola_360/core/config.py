from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    app_name: str = "OLA 360"
    subtitle: str = "Executive PMO Chief of Staff"
    tagline: str = "Executive clarity. Every morning."
    db_path: Path = ROOT_DIR / "data" / "ola_360.db"
    session_timeout_minutes: int = 45
    default_language: str = "en"
    default_theme: str = "dark"


def load_settings() -> Settings:
    configured = Path(os.getenv("OLA_360_DB_PATH", str(ROOT_DIR / "data" / "ola_360.db")))
    db_path = _writable_db_path(configured)
    timeout = int(os.getenv("OLA_360_SESSION_TIMEOUT_MINUTES", "45"))
    return Settings(db_path=db_path, session_timeout_minutes=timeout)


def _writable_db_path(configured: Path) -> Path:
    try:
        configured.parent.mkdir(parents=True, exist_ok=True)
        probe = configured.parent / ".ola_360_write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return configured
    except OSError:
        runtime = Path(tempfile.gettempdir()) / "ola360_runtime" / "data"
        runtime.mkdir(parents=True, exist_ok=True)
        return runtime / "ola_360_runtime.db"
