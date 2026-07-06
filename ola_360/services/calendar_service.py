from __future__ import annotations

import os
import re
from urllib.request import urlopen

from ola_360.repositories.app_repository import AppRepository


class CalendarService:
    def __init__(self, repo: AppRepository):
        self.repo = repo

    def import_ics_from_env(self) -> dict[str, object]:
        url = os.getenv("OLA_CALENDAR_ICS_URL")
        if not url:
            return {"imported": 0, "status": "OLA_CALENDAR_ICS_URL is not configured."}
        with urlopen(url, timeout=30) as response:
            content = response.read().decode("utf-8", errors="replace")
        return self.import_ics(content, source=url)

    def import_ics(self, content: str, source: str = "ICS") -> dict[str, object]:
        imported = 0
        for block in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", content, flags=re.S):
            title = self._field(block, "SUMMARY") or "Calendar meeting"
            start = self._field(block, "DTSTART") or ""
            end = self._field(block, "DTEND") or ""
            uid = self._field(block, "UID") or f"{source}:{title}:{start}"
            if start:
                self.repo.create_calendar_event(uid, title, self._normalise_ics_time(start), self._normalise_ics_time(end), source)
                self.repo.create_meeting(title, "Calendar meeting", self._normalise_ics_time(start)[:10], f"Imported from calendar source: {source}")
                imported += 1
        return {"imported": imported, "status": f"Imported {imported} calendar event(s)."}

    def _field(self, block: str, name: str) -> str:
        match = re.search(rf"^{name}(?:;[^:]*)?:(.+)$", block, flags=re.M)
        return match.group(1).strip() if match else ""

    def _normalise_ics_time(self, value: str) -> str:
        match = re.match(r"(\d{4})(\d{2})(\d{2})T?(\d{2})?(\d{2})?", value)
        if not match:
            return value
        y, m, d, hh, mm = match.groups()
        return f"{y}-{m}-{d}" + (f" {hh or '00'}:{mm or '00'}" if hh else "")
