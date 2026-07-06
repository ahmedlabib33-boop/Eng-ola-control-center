from __future__ import annotations

from datetime import date, datetime

from ola_360.repositories.app_repository import AppRepository
from ola_360.services.escalation_service import EscalationService
from ola_360.services.portfolio_service import PortfolioService


class MorningBriefService:
    def __init__(self, repo: AppRepository):
        self.repo = repo

    def build(self) -> dict:
        warnings = self.repo.warnings()
        commitments = self.repo.commitments()
        decisions = self.repo.decisions()
        meetings = self.repo.meetings()
        escalations = EscalationService(self.repo).overdue_escalations()
        portfolio = PortfolioService(self.repo).rollup()
        critical = [w for w in warnings if w.severity == "Critical" and w.status != "Closed"]
        overdue = [c for c in commitments if c.due_date < date.today().isoformat() and c.status != "Completed"]
        pending_decisions = [d for d in decisions if d.status == "Pending"]
        if critical or overdue or pending_decisions:
            summary = (
                f"{len(critical)} critical warning(s), {len(overdue)} overdue commitment(s), "
                f"and {len(pending_decisions)} decision(s) require attention today."
            )
        else:
            summary = "Stored PMO data shows no critical exception requiring immediate intervention."
        return {
            "date": date.today().strftime("%A, %d %B %Y"),
            "time": datetime.now().strftime("%H:%M"),
            "summary": summary,
            "critical_count": len(critical),
            "overdue_count": len(overdue),
            "decision_count": len(pending_decisions),
            "meetings": meetings,
            "warnings": critical[:3],
            "escalations": escalations[:3],
            "portfolio": portfolio,
            "personal_preview": self.repo.private_tasks()[:1],
            "freshness": f"Local data refreshed {datetime.now().strftime('%H:%M')}",
        }
