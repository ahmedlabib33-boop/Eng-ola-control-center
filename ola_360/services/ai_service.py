from __future__ import annotations

import re
from datetime import date, datetime, timedelta

from ola_360.repositories.app_repository import AppRepository


class AIService:
    def __init__(self, repo: AppRepository):
        self.repo = repo

    def answer(self, prompt: str, include_private: bool = False) -> dict[str, str]:
        context = self.repo.ai_records_context(include_private=include_private)
        prompt_lower = prompt.lower()
        facts: list[str] = []
        if "overdue" in prompt_lower or "attention" in prompt_lower or "today" in prompt_lower:
            overdue = [c for c in context["commitments"] if c["status"] == "Overdue"]
            critical = [w for w in context["warnings"] if w["severity"] == "Critical" and w["status"] != "Closed"]
            facts.append(f"{len(critical)} critical warning(s) and {len(overdue)} overdue commitment(s) are stored.")
            for item in critical[:2]:
                facts.append(f"Warning: {item['title']} | Owner: {item['owner']} | Due: {item['due_date']}")
            for item in overdue[:2]:
                facts.append(f"Commitment: {item['title']} | Owner: {item['owner']} | Due: {item['due_date']}")
        elif "meeting" in prompt_lower or "agenda" in prompt_lower:
            meetings = context["meetings"]
            facts.append(f"{len(meetings)} meeting(s) are stored. Add open warnings and overdue commitments to the next agenda.")
        elif "arabic" in prompt_lower or "عربي" in prompt_lower:
            facts.append("الرد مبني فقط على البيانات المخزنة داخل التطبيق ولا يتضمن معلومات غير مؤكدة.")
        else:
            facts.append("I can answer from stored warnings, commitments, decisions, and meetings. No external facts were used.")
        if not include_private:
            facts.append("Private My Day records are excluded from this organizational answer.")
        return {
            "answer": "\n".join(facts),
            "confidence": "Medium",
            "sources": "Local SQLite records",
            "missing": "Connect OpenAI or Ollama for richer language generation; fallback remains rule-based.",
            "fact_vs_inference": "Facts come from stored records. Recommendations are rule-based inference.",
        }

    def extract_meeting_intelligence(self, notes: str, title: str = "Executive meeting") -> dict[str, str]:
        lines = [line.strip("- *\t ") for line in notes.splitlines() if line.strip()]
        if not lines:
            lines = ["No discussion text was provided. Add notes or recording transcript before approval."]
        labels = self._parse_labeled_meeting_lines(lines)

        def first_matching(words: list[str], fallback: str) -> str:
            for line in lines:
                if any(word in line.lower() for word in words):
                    return self._strip_leading_label(line)
            return fallback

        decision = labels.get("decision") or first_matching(["decision", "decide", "approved", "agreed"], "Decision not detected. Review transcript and add the confirmed decision.")
        action = labels.get("action_required") or first_matching(["action", "submit", "prepare", "follow", "send"], "Action not detected. Add required action before saving.")
        warning = labels.get("related_warning") or first_matching(["warning", "risk", "delay", "overdue", "critical"], "No related warning detected.")
        project = labels.get("related_project") or first_matching(["project", "building", "tunnel", "road", "infrastructure"], "Configured PMO Project")
        due_date = labels.get("due_date") or self._first_date(lines) or (date.today() + timedelta(days=3)).isoformat()
        owner = labels.get("responsible_person") or labels.get("owner") or self._owner_from_action(action) or "Project Manager"
        priority = labels.get("priority") or ("Critical" if any(word in " ".join(lines).lower() for word in ["critical", "overdue", "delay", "urgent"]) else "Medium")
        summary = labels.get("discussion_summary") or " ".join(self._strip_leading_label(line) for line in lines[:3])
        attachment = labels.get("supporting_attachment") or "No attachment linked. Add evidence before closure if required."

        minutes = (
            f"Meeting: {title}\n"
            f"Discussion summary: {summary}\n"
            f"Decision: {decision}\n"
            f"Action required: {action}\n"
            f"Responsible person: {owner}\n"
            f"Due date: {due_date}\n"
            f"Priority: {priority}\n"
            f"Related project: {project}\n"
            f"Related warning: {warning}\n"
            "Review status: Draft requires Eng. Ola approval before saving or sending."
        )
        overdue_actions = [
            f"- {item.title} | Owner: {item.owner} | Due: {item.due_date}"
            for item in self.repo.commitments()
            if item.status.lower() == "overdue"
        ]
        return {
            "discussion_summary": summary,
            "decision": decision,
            "action_required": action,
            "responsible_person": owner,
            "due_date": due_date,
            "priority": priority,
            "related_project": project,
            "related_warning": warning,
            "supporting_attachment": attachment,
            "meeting_minutes": minutes,
            "action_register": f"{action} | Owner: {owner} | Due: {due_date} | Priority: {priority} | Status: Draft",
            "decision_register": f"{decision} | Project: {project} | Status: Draft pending approval",
            "follow_up_email_draft": (
                f"Subject: Follow-up actions - {title}\n\n"
                f"Dear Team,\n\nFollowing today's discussion, please note the required action:\n"
                f"- {action}\nOwner: {owner}\nDue date: {due_date}\nPriority: {priority}\n\n"
                "Please provide evidence of closure before the due date.\n\nRegards,\nEng. Ola"
            ),
            "next_meeting_agenda": f"1. Review closure evidence for: {action}\n2. Confirm decision implementation: {decision}\n3. Review related warning: {warning}",
            "overdue_action_list": "\n".join(overdue_actions) or "No overdue stored actions.",
        }

    def extract_meeting_notes(self, notes: str) -> dict[str, list[str]]:
        lines = [line.strip("- *\t ") for line in notes.splitlines() if line.strip()]
        actions = [line for line in lines if any(word in line.lower() for word in ["action", "todo", "submit", "prepare", "follow"])]
        decisions = [line for line in lines if any(word in line.lower() for word in ["decide", "approved", "decision", "agreed"])]
        return {
            "summary": lines[:4],
            "proposed_actions": actions,
            "proposed_decisions": decisions,
            "review_required": ["User approval required before saving extracted actions."],
        }

    def _parse_labeled_meeting_lines(self, lines: list[str]) -> dict[str, str]:
        aliases = {
            "discussion summary": "discussion_summary",
            "summary": "discussion_summary",
            "decision": "decision",
            "action required": "action_required",
            "action": "action_required",
            "responsible person": "responsible_person",
            "responsible": "responsible_person",
            "owner": "owner",
            "due date": "due_date",
            "due": "due_date",
            "priority": "priority",
            "related project": "related_project",
            "project": "related_project",
            "related warning": "related_warning",
            "warning": "related_warning",
            "supporting attachment": "supporting_attachment",
            "attachment": "supporting_attachment",
        }
        parsed: dict[str, str] = {}
        for line in lines:
            match = re.match(r"^\s*([A-Za-z ]{3,28})\s*[:=-]\s*(.+?)\s*$", line)
            if not match:
                continue
            key = aliases.get(match.group(1).strip().lower())
            if key and match.group(2).strip():
                parsed[key] = self._normalise_field_value(key, match.group(2).strip())
        return parsed

    def _normalise_field_value(self, key: str, value: str) -> str:
        if key == "due_date":
            parsed = self._normalise_date(value)
            return parsed or value
        if key == "priority":
            lowered = value.lower()
            if "critical" in lowered:
                return "Critical"
            if "high" in lowered:
                return "High"
            if "low" in lowered:
                return "Low"
            return "Medium"
        return value

    def _normalise_date(self, value: str) -> str | None:
        compact = re.search(r"\b(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\b", value)
        if compact:
            return date(int(compact.group(1)), int(compact.group(2)), int(compact.group(3))).isoformat()
        day_month = re.search(r"\b(\d{1,2})[-/](\d{1,2})[-/](20\d{2})\b", value)
        if day_month:
            return date(int(day_month.group(3)), int(day_month.group(2)), int(day_month.group(1))).isoformat()
        month_name = re.search(r"\b(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})\b", value)
        if month_name:
            try:
                return datetime.strptime(month_name.group(0), "%d %B %Y").date().isoformat()
            except ValueError:
                try:
                    return datetime.strptime(month_name.group(0), "%d %b %Y").date().isoformat()
                except ValueError:
                    return None
        return None

    def _first_date(self, lines: list[str]) -> str | None:
        for line in lines:
            parsed = self._normalise_date(line)
            if parsed:
                return parsed
        return None

    def _strip_leading_label(self, line: str) -> str:
        return re.sub(r"^\s*[A-Za-z ]{3,28}\s*[:=-]\s*", "", line).strip()

    def _owner_from_action(self, action: str) -> str | None:
        match = re.search(r"\b(?:owner|responsible|by)\s*[:=-]?\s*([A-Z][A-Za-z .'-]{2,40})", action)
        if match:
            return match.group(1).strip()
        return None
