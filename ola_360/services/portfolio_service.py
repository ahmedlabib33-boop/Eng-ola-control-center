from __future__ import annotations

from collections import defaultdict
from datetime import date

from ola_360.repositories.app_repository import AppRepository


class PortfolioService:
    def __init__(self, repo: AppRepository):
        self.repo = repo

    def rollup(self) -> dict[str, object]:
        warnings = [w for w in self.repo.warnings() if w.status != "Closed"]
        commitments = [c for c in self.repo.commitments() if c.status != "Completed"]
        updates = self.repo.project_updates()
        by_project: dict[str, dict[str, object]] = defaultdict(lambda: {"critical": 0, "watch": 0, "overdue": 0, "latest_progress": None, "sector": "Other"})
        for warning in warnings:
            row = by_project[warning.project]
            row["sector"] = warning.sector
            if warning.severity == "Critical":
                row["critical"] = int(row["critical"]) + 1
            elif warning.severity in {"Watch", "Intervention"}:
                row["watch"] = int(row["watch"]) + 1
        today = date.today().isoformat()
        for commitment in commitments:
            row = by_project[commitment.project]
            if commitment.due_date < today:
                row["overdue"] = int(row["overdue"]) + 1
        latest: dict[str, object] = {}
        for update in updates:
            current = latest.get(update.project)
            if current is None or update.update_date > current.update_date:
                latest[update.project] = update
        for project, update in latest.items():
            row = by_project[project]
            row["sector"] = update.sector
            row["latest_progress"] = update.progress
        project_rows: list[dict[str, object]] = []
        red = amber = green = 0
        for project, row in sorted(by_project.items()):
            status = "Green"
            if int(row["critical"]) or int(row["overdue"]) >= 2:
                status = "Red"
                red += 1
            elif int(row["watch"]) or int(row["overdue"]):
                status = "Amber"
                amber += 1
            else:
                green += 1
            project_rows.append({"project": project, "status": status, **row})
        return {
            "red_projects": red,
            "amber_projects": amber,
            "green_projects": green,
            "open_warnings": len(warnings),
            "open_commitments": len(commitments),
            "projects": project_rows,
        }

    def predictive_flags(self) -> list[dict[str, str]]:
        flags: list[dict[str, str]] = []
        updates_by_project: dict[str, list[object]] = defaultdict(list)
        for update in self.repo.project_updates():
            updates_by_project[update.project].append(update)
        for project, updates in updates_by_project.items():
            ordered = sorted(updates, key=lambda item: item.update_date)
            if len(ordered) >= 2:
                delta = ordered[-1].progress - ordered[-2].progress
                if delta <= 0:
                    flags.append({"project": project, "signal": "Progress is flat or deteriorating", "basis": f"Latest progress delta: {delta}%"})
                elif delta < 3 and any(term in ordered[-1].issues.lower() for term in ["delay", "risk", "procurement", "critical"]):
                    flags.append({"project": project, "signal": "Low progress gain with risk language", "basis": ordered[-1].issues})
            elif ordered and any(term in ordered[-1].issues.lower() for term in ["delay", "risk", "procurement", "critical"]):
                flags.append({"project": project, "signal": "Risk language detected in latest update", "basis": ordered[-1].issues})
        return flags
