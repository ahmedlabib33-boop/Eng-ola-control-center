from __future__ import annotations

from datetime import date

from ola_360.repositories.app_repository import AppRepository


class EscalationService:
    def __init__(self, repo: AppRepository, threshold_days: int = 2):
        self.repo = repo
        self.threshold_days = threshold_days

    def overdue_escalations(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        today = date.today()
        for item in self.repo.commitments():
            if item.status == "Completed":
                continue
            try:
                days_overdue = (today - date.fromisoformat(item.due_date)).days
            except ValueError:
                continue
            if days_overdue > 0:
                level = 1 if days_overdue < self.threshold_days else 2
                if days_overdue >= self.threshold_days * 3:
                    level = 3
                rows.append(
                    {
                        "id": item.id,
                        "title": item.title,
                        "owner": item.owner,
                        "project": item.project,
                        "due_date": item.due_date,
                        "days_overdue": days_overdue,
                        "level": level,
                        "suggested_nudge": self.nudge_message(item.title, item.owner, item.project, item.due_date, days_overdue, level),
                    }
                )
        return rows

    def nudge_message(self, title: str, owner: str, project: str, due_date: str, days_overdue: int, level: int) -> str:
        prefix = "Escalation" if level >= 2 else "Reminder"
        return (
            f"Subject: {prefix}: overdue commitment - {project}\n\n"
            f"Dear {owner},\n\n"
            f"The commitment '{title}' was due on {due_date} and is now {days_overdue} day(s) overdue. "
            "Please send the closure evidence or a recovery date today.\n\n"
            "Regards,\nEng. Ola"
        )
