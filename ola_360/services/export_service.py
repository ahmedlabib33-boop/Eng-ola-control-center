from __future__ import annotations

import csv
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from ola_360.repositories.app_repository import AppRepository


class ExportService:
    def __init__(self, repo: AppRepository, export_dir: Path):
        self.repo = repo
        self.export_dir = export_dir

    def export(self, dataset: str) -> Path:
        exporters = {
            "projects": self.repo.projects,
            "warnings": self.repo.warnings,
            "warning_evidence": self.repo.warning_evidence,
            "meetings": self.repo.meetings,
            "attendees": self.repo.attendees,
            "agenda_items": self.repo.agenda_items,
            "commitments": self.repo.commitments,
            "decisions": self.repo.decisions,
            "milestones": self.repo.milestones,
            "project_updates": self.repo.project_updates,
            "comments": self.repo.comments,
            "attachments": self.repo.attachments,
            "private_tasks": self.repo.private_tasks,
            "personal_events": self.repo.personal_events,
            "private_notes": self.repo.private_notes,
            "wellbeing_checkins": self.repo.wellbeing_checkins,
        }
        if dataset not in exporters:
            raise ValueError(f"Unsupported export dataset: {dataset}")
        rows = self._rows(exporters[dataset]())
        self.export_dir.mkdir(parents=True, exist_ok=True)
        output = self.export_dir / f"{dataset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        headers = sorted({key for row in rows for key in row.keys()})
        with output.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        return output

    def _rows(self, records: Iterable[object]) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for record in records:
            if is_dataclass(record):
                rows.append(asdict(record))
            elif isinstance(record, dict):
                rows.append(record)
            else:
                rows.append(dict(record))
        return rows
