from __future__ import annotations

from datetime import datetime


class OfflineService:
    def __init__(self) -> None:
        self.last_sync = datetime.now()
        self.queue: list[str] = []

    def status(self, offline: bool = False) -> dict[str, str]:
        return {
            "mode": "Offline" if offline else "Online",
            "last_sync": self.last_sync.strftime("%Y-%m-%d %H:%M"),
            "queued_updates": str(len(self.queue)),
        }

    def queue_update(self, description: str) -> None:
        self.queue.append(description)
