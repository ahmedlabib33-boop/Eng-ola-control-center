from __future__ import annotations

import logging
import tempfile
from pathlib import Path


def configure_logging(root: Path) -> None:
    log_format = "%(asctime)s %(levelname)s %(name)s %(message)s"
    try:
        log_dir = root / "logs"
        log_dir.mkdir(exist_ok=True)
        logging.basicConfig(filename=log_dir / "ola_360.log", level=logging.INFO, format=log_format, force=True)
    except OSError:
        fallback = Path(tempfile.gettempdir()) / "ola360_runtime" / "logs"
        try:
            fallback.mkdir(parents=True, exist_ok=True)
            logging.basicConfig(filename=fallback / "ola_360.log", level=logging.INFO, format=log_format, force=True)
        except OSError:
            logging.basicConfig(level=logging.INFO, format=log_format, force=True)
