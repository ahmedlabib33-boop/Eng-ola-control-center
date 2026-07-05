from __future__ import annotations

from datetime import date, timedelta

from ola_360.repositories.app_repository import AppRepository


class NotificationService:
    def __init__(self, repo: AppRepository):
        self.repo = repo

    def build_notifications(self) -> list[str]:
        items: list[str] = []
        for warning in self.repo.warnings():
            if warning.severity == "Critical" and warning.status != "Closed":
                items.append(f"Critical warning: {warning.title}")
        for commitment in self.repo.commitments():
            if commitment.due_date <= date.today().isoformat() and commitment.status != "Completed":
                items.append(f"Commitment due: {commitment.title}")
        for decision in self.repo.decisions():
            if decision.status == "Pending":
                items.append(f"Decision pending: {decision.title}")
        freshness_limit = date.today() - timedelta(days=7)
        latest_by_project: dict[str, str] = {}
        for update in self.repo.project_updates():
            latest_by_project.setdefault(update.project, update.update_date)
        for project, update_date in latest_by_project.items():
            if update_date < freshness_limit.isoformat():
                items.append(f"Missing recent project update: {project}")
        if not latest_by_project:
            items.append("Missing project updates: no PMO project update records are stored")
        for task in self.repo.private_tasks():
            if task.due_date <= date.today().isoformat():
                items.append(f"Private reminder: {task.title}")
        return items
