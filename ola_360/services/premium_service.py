from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

from ola_360.repositories.app_repository import AppRepository


class PremiumService:
    def __init__(self, repo: AppRepository):
        self.repo = repo

    def executive_focus(self) -> list[dict[str, str]]:
        items: list[dict[str, str]] = []
        for warning in self.repo.warnings():
            if warning.status != "Closed" and warning.severity in {"Critical", "Intervention"}:
                items.append(
                    {
                        "kind": "Warning",
                        "title": warning.title,
                        "detail": f"{warning.project} | {warning.sector} | Owner: {warning.owner}",
                        "action": warning.recommended_intervention,
                        "due": warning.due_date,
                        "severity": warning.severity,
                    }
                )
        for commitment in self.repo.commitments():
            if commitment.status in {"Overdue", "Escalated"} or self._is_due_or_late(commitment.due_date):
                items.append(
                    {
                        "kind": "Commitment",
                        "title": commitment.title,
                        "detail": f"{commitment.project} | Owner: {commitment.owner}",
                        "action": "Close, escalate, or request evidence.",
                        "due": commitment.due_date,
                        "severity": commitment.priority,
                    }
                )
        for decision in self.repo.decisions():
            if decision.status in {"Pending", "Deferred"}:
                items.append(
                    {
                        "kind": "Decision",
                        "title": decision.title,
                        "detail": decision.project,
                        "action": "Approve, defer, or request clarification.",
                        "due": decision.due_date,
                        "severity": decision.status,
                    }
                )
        return sorted(items, key=lambda item: (item["due"], item["kind"]))[:3]

    def intervention_items(self) -> list[dict[str, str]]:
        items = self.executive_focus()
        for update in self.repo.project_updates()[:5]:
            if update.issues.strip():
                items.append(
                    {
                        "kind": "Project Update",
                        "title": update.project,
                        "detail": f"{update.sector} | Progress {update.progress}%",
                        "action": update.issues,
                        "due": update.update_date,
                        "severity": "Data",
                    }
                )
        return items

    def template_catalog(self) -> list[dict[str, str]]:
        templates_dir = self.repo.db_path.parents[1] / "templates"
        if not templates_dir.exists():
            templates_dir = Path.cwd() / "templates"
        descriptions = {
            "warnings_template.csv": "Early-warning radar records",
            "warning_evidence_template.csv": "Evidence linked to warning IDs",
            "critical_issues_template.csv": "Critical issues imported as warnings",
            "projects_template.csv": "Project master data",
            "project_updates_template.csv": "Progress and freshness updates",
            "meetings_template.csv": "Meeting records",
            "attendees_template.csv": "Meeting attendees",
            "agenda_items_template.csv": "Meeting agenda items",
            "commitments_template.csv": "Action register",
            "decisions_template.csv": "Decision register",
            "milestones_template.csv": "Milestone register",
            "comments_template.csv": "Evidence comments",
            "attachments_template.csv": "Attachment references",
            "personal_tasks_template.csv": "Private My Day tasks",
            "personal_events_template.csv": "Private events and reminders",
            "private_notes_template.csv": "Private notes and ideas",
            "wellbeing_checkins_template.csv": "Non-medical wellbeing check-ins",
            "meeting_notes_template.txt": "Meeting extraction paste sample",
        }
        rows: list[dict[str, str]] = []
        for path in sorted(templates_dir.glob("*_template.*")):
            rows.append(
                {
                    "name": path.name,
                    "description": descriptions.get(path.name, "Structured data input template"),
                    "path": str(path),
                    "type": "Text" if path.suffix.lower() == ".txt" else "CSV/XLSX headers",
                }
            )
        return rows

    def shutdown_review(self) -> dict[str, Any]:
        today = date.today().isoformat()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        commitments = self.repo.commitments()
        decisions = self.repo.decisions()
        warnings = self.repo.warnings()
        personal = self.repo.private_tasks()
        open_commitments = [item for item in commitments if item.status != "Completed"]
        overdue = [item for item in open_commitments if item.due_date <= today or item.status == "Overdue"]
        return {
            "completed_today": [item.title for item in commitments if item.status == "Completed"][:5],
            "still_open": [item.title for item in open_commitments[:5]],
            "overdue": [item.title for item in overdue[:5]],
            "pending_decisions": [item.title for item in decisions if item.status in {"Pending", "Deferred"}][:5],
            "director_attention": [item.title for item in warnings if item.severity == "Critical" and item.status != "Closed"][:5],
            "personal_attention": [item.title for item in personal if item.due_date <= tomorrow and item.status != "Closed"][:5],
            "tomorrow_priority": self._tomorrow_priority(warnings, open_commitments, decisions),
        }

    def recent_timeline(self, limit: int = 12) -> list[dict[str, str]]:
        return self.repo.audit_logs(limit=limit)

    def _tomorrow_priority(self, warnings: list[Any], commitments: list[Any], decisions: list[Any]) -> str:
        critical = [item for item in warnings if item.severity == "Critical" and item.status != "Closed"]
        if critical:
            return f"Resolve director intervention: {critical[0].title}"
        if commitments:
            return f"Close commitment: {commitments[0].title}"
        pending = [item for item in decisions if item.status in {"Pending", "Deferred"}]
        if pending:
            return f"Decide: {pending[0].title}"
        return "Review Morning Brief and confirm no new critical item."

    def _is_due_or_late(self, value: str) -> bool:
        try:
            return date.fromisoformat(value) <= date.today()
        except ValueError:
            return False
