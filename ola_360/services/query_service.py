from __future__ import annotations

from ola_360.repositories.app_repository import AppRepository


class NaturalQueryService:
    def __init__(self, repo: AppRepository):
        self.repo = repo

    def answer(self, prompt: str) -> str:
        text = prompt.lower()
        project_filter = self._project_from_prompt(prompt)
        lines: list[str] = []
        if "overdue" in text or "actions" in text or "commitments" in text:
            rows = [c for c in self.repo.commitments() if c.status != "Completed"]
            if project_filter:
                rows = [c for c in rows if project_filter.lower() in c.project.lower()]
            rows = [c for c in rows if c.status == "Overdue" or c.due_date < self._today()]
            lines.extend(f"- {c.title} | {c.project} | Owner: {c.owner} | Due: {c.due_date}" for c in rows)
            return "\n".join(lines) or "No matching overdue actions are stored."
        if "decision" in text:
            rows = self.repo.decisions()
            if project_filter:
                rows = [d for d in rows if project_filter.lower() in d.project.lower()]
            lines.extend(f"- {d.title} | {d.project} | {d.status} | Due: {d.due_date}" for d in rows)
            return "\n".join(lines) or "No matching decisions are stored."
        if "warning" in text or "risk" in text:
            rows = self.repo.warnings()
            if project_filter:
                rows = [w for w in rows if project_filter.lower() in w.project.lower()]
            lines.extend(f"- {w.title} | {w.project} | {w.severity} | {w.trend}" for w in rows)
            return "\n".join(lines) or "No matching warnings are stored."
        return "Ask about stored overdue actions, decisions, warnings, or risks. Private data is excluded."

    def _project_from_prompt(self, prompt: str) -> str:
        lowered = prompt.lower()
        for marker in ["project ", "related to ", "for "]:
            if marker in lowered:
                return prompt[lowered.index(marker) + len(marker) :].strip(" ?.")[:80]
        return ""

    def _today(self) -> str:
        from datetime import date

        return date.today().isoformat()
