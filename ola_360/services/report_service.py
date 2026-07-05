from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from ola_360.repositories.app_repository import AppRepository


class ReportService:
    def __init__(self, repo: AppRepository, export_dir: Path):
        self.repo = repo
        self.export_dir = export_dir

    def build_executive_report(self) -> Path:
        self.export_dir.mkdir(parents=True, exist_ok=True)
        output = self.export_dir / f"executive_pmo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        warnings = [item for item in self.repo.warnings() if item.status != "Closed"]
        critical = [item for item in warnings if item.severity == "Critical"]
        overdue = [item for item in self.repo.commitments() if item.status == "Overdue" or self._is_overdue(item.due_date, item.status)]
        decisions = [item for item in self.repo.decisions() if item.status in {"Pending", "Deferred"}]
        meetings = self.repo.meetings()
        updates = self.repo.project_updates()
        comments = self.repo.comments()
        attachments = self.repo.attachments()

        lines = [
            "# OLA 360 Executive PMO Report",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "Prepared for: Eng. Ola",
            "",
            "## Executive Snapshot",
            "",
            f"- Open warnings: {len(warnings)}",
            f"- Critical warnings: {len(critical)}",
            f"- Overdue commitments: {len(overdue)}",
            f"- Decisions awaiting closure: {len(decisions)}",
            f"- Stored meetings: {len(meetings)}",
            f"- Project updates: {len(updates)}",
            "",
            "## Executive Summary",
            "",
            self._summary(len(critical), len(overdue), len(decisions), len(updates)),
            "",
            "## Critical Warnings",
            "",
            *self._warning_lines(critical),
            "",
            "## Overdue Commitments",
            "",
            *self._commitment_lines(overdue),
            "",
            "## Decisions Awaiting Closure",
            "",
            *self._decision_lines(decisions),
            "",
            "## Recent Meetings",
            "",
            *self._meeting_lines(meetings),
            "",
            "## Project Updates And Evidence",
            "",
            *self._update_lines(updates),
            "",
            f"- Comments stored as evidence context: {len(comments)}",
            f"- Attachment references stored: {len(attachments)}",
            "",
            "## Privacy Boundary",
            "",
            "My Day private tasks, personal events, private notes, and wellbeing check-ins are intentionally excluded from this PMO report.",
            "",
            "## Data Sources",
            "",
            "Local SQLite records: warnings, commitments, decisions, meetings, project updates, comments, and attachments.",
        ]
        output.write_text("\n".join(lines), encoding="utf-8")
        return output

    def _summary(self, critical_count: int, overdue_count: int, decision_count: int, update_count: int) -> str:
        parts: list[str] = []
        if critical_count:
            parts.append(f"{critical_count} critical warning(s) require executive attention.")
        if overdue_count:
            parts.append(f"{overdue_count} commitment(s) are overdue or past due.")
        if decision_count:
            parts.append(f"{decision_count} decision(s) remain pending or deferred.")
        if update_count == 0:
            parts.append("No project updates are stored, so data freshness is weak.")
        return " ".join(parts) or "No critical stored issue is currently visible in the PMO dataset."

    def _warning_lines(self, warnings: list[object]) -> list[str]:
        if not warnings:
            return ["No critical warning is currently stored."]
        return [
            f"- {item.title} | {item.project} | {item.sector} | Owner: {item.owner} | Due: {item.due_date} | Trend: {item.trend}"
            for item in warnings[:10]
        ]

    def _commitment_lines(self, commitments: list[object]) -> list[str]:
        if not commitments:
            return ["No overdue commitment is currently stored."]
        return [
            f"- {item.title} | Owner: {item.owner} | Project: {item.project} | Due: {item.due_date} | Priority: {item.priority}"
            for item in commitments[:10]
        ]

    def _decision_lines(self, decisions: list[object]) -> list[str]:
        if not decisions:
            return ["No pending or deferred decision is currently stored."]
        return [
            f"- {item.title} | Project: {item.project} | Status: {item.status} | Due: {item.due_date}"
            for item in decisions[:10]
        ]

    def _meeting_lines(self, meetings: list[object]) -> list[str]:
        if not meetings:
            return ["No meeting record is currently stored."]
        return [
            f"- {item.meeting_date} | {item.title} | {item.meeting_type} | Status: {item.status}"
            for item in meetings[:10]
        ]

    def _update_lines(self, updates: list[object]) -> list[str]:
        if not updates:
            return ["No project update is currently stored."]
        return [
            f"- {item.project} | {item.sector} | {item.update_date} | Progress: {item.progress}% | {item.summary}"
            for item in updates[:10]
        ]

    def _is_overdue(self, due_date: str, status: str) -> bool:
        if status == "Completed":
            return False
        try:
            return date.fromisoformat(due_date) < date.today()
        except ValueError:
            return False
