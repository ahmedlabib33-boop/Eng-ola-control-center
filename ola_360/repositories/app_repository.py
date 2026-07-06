from __future__ import annotations

import csv
import sqlite3
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from ola_360.models.entities import (
    AgendaItem,
    Attachment,
    Attendee,
    Comment,
    Commitment,
    Decision,
    Meeting,
    Milestone,
    PersonalEvent,
    PersonalTask,
    PrivateNote,
    Project,
    ProjectUpdate,
    User,
    WarningItem,
    WarningEvidence,
    WellbeingCheckin,
)
from ola_360.repositories.database import connect


class AppRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def _conn(self) -> sqlite3.Connection:
        return connect(self.db_path)

    def get_user_by_email(self, email: str) -> sqlite3.Row | None:
        with self._conn() as conn:
            return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    def create_user(self, name: str, email: str, password_hash: str, role: str) -> int:
        if role not in {"Executive", "PMO Admin", "Deputy", "PMO Analyst"}:
            raise ValueError("Unsupported role")
        with self._conn() as conn:
            conn.execute("INSERT OR IGNORE INTO roles(name) VALUES (?)", (role,))
            cur = conn.execute(
                """
                INSERT INTO users(name, email, password_hash, role)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(email) DO UPDATE SET name=excluded.name, role=excluded.role
                """,
                (name, email, password_hash, role),
            )
            user = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            return int(user["id"] if user else cur.lastrowid)

    def sectors(self) -> list[str]:
        with self._conn() as conn:
            rows = conn.execute("SELECT name FROM sectors ORDER BY name").fetchall()
        return [str(row["name"]) for row in rows]

    def projects(self) -> list[Project]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT projects.id, projects.name, COALESCE(sectors.name, 'Other') AS sector, projects.status
                FROM projects
                LEFT JOIN sectors ON sectors.id = projects.sector_id
                ORDER BY projects.name
                """
            ).fetchall()
        return [Project(**dict(row)) for row in rows]

    def create_project_from_data(self, data: dict[str, Any]) -> int:
        name = str(data.get("name", data.get("project", ""))).strip()
        if not name:
            raise ValueError("Project name is required")
        sector_name = str(data.get("sector", "Other") or "Other")
        with self._conn() as conn:
            sector = conn.execute("SELECT id FROM sectors WHERE name = ?", (sector_name,)).fetchone()
            if sector:
                sector_id = int(sector["id"])
            else:
                cur_sector = conn.execute("INSERT INTO sectors(name) VALUES (?)", (sector_name,))
                sector_id = int(cur_sector.lastrowid)
            existing = conn.execute("SELECT id FROM projects WHERE name = ?", (name,)).fetchone()
            if existing:
                conn.execute("UPDATE projects SET sector_id = ?, status = ? WHERE id = ?", (sector_id, data.get("status", "Active"), existing["id"]))
                project_id = int(existing["id"])
            else:
                cur = conn.execute("INSERT INTO projects(name, sector_id, status) VALUES (?, ?, ?)", (name, sector_id, data.get("status", "Active")))
                project_id = int(cur.lastrowid)
            conn.execute("INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)", ("Eng. Ola", "upsert", "project", project_id))
            return project_id

    def warnings(self, sector: str = "All", severity: str = "All") -> list[WarningItem]:
        query = "SELECT * FROM warnings WHERE 1=1"
        params: list[Any] = []
        if sector != "All":
            query += " AND sector = ?"
            params.append(sector)
        if severity != "All":
            query += " AND severity = ?"
            params.append(severity)
        query += " ORDER BY CASE severity WHEN 'Critical' THEN 1 WHEN 'Intervention' THEN 2 WHEN 'Watch' THEN 3 ELSE 4 END, due_date"
        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
        return [WarningItem(**dict(row)) for row in rows]

    def create_warning(self, data: dict[str, Any]) -> int:
        required = ["title", "category", "sector", "project", "severity", "trend", "owner", "due_date"]
        missing = [key for key in required if not str(data.get(key, "")).strip()]
        if missing:
            raise ValueError(f"Missing warning fields: {', '.join(missing)}")
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO warnings(
                    title, category, sector, project, severity, trend, evidence,
                    potential_impact, impacted_milestone, owner, date_identified, due_date,
                    recommended_intervention, source, last_update, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open')
                """,
                (
                    data["title"],
                    data["category"],
                    data["sector"],
                    data["project"],
                    data["severity"],
                    data["trend"],
                    data.get("evidence", "Manual entry pending evidence."),
                    data.get("potential_impact", "Impact to be assessed."),
                    data.get("impacted_milestone", ""),
                    data["owner"],
                    data.get("date_identified", date.today().isoformat()),
                    data["due_date"],
                    data.get("recommended_intervention", "Review and assign owner."),
                    data.get("source", "Manual entry"),
                    datetime.now(UTC).isoformat(),
                ),
            )
            conn.execute("INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)", ("Eng. Ola", "create", "warning", cur.lastrowid))
            return int(cur.lastrowid)

    def update_warning_status(self, warning_id: int, status: str) -> None:
        with self._conn() as conn:
            conn.execute("UPDATE warnings SET status = ?, last_update = ? WHERE id = ?", (status, datetime.now(UTC).isoformat(), warning_id))
            conn.execute("INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)", ("Eng. Ola", f"status:{status}", "warning", warning_id))

    def update_warning_core(self, warning_id: int, title: str, owner: str, due_date: str) -> None:
        if not title.strip() or not owner.strip() or not due_date.strip():
            raise ValueError("Warning title, owner, and due date are required")
        with self._conn() as conn:
            conn.execute(
                "UPDATE warnings SET title = ?, owner = ?, due_date = ?, last_update = ? WHERE id = ?",
                (title, owner, due_date, datetime.now(UTC).isoformat(), warning_id),
            )
            conn.execute("INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)", ("Eng. Ola", "edit", "warning", warning_id))

    def warning_evidence(self) -> list[WarningEvidence]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id, warning_id, evidence_text, source, created_at FROM warning_evidence ORDER BY created_at DESC").fetchall()
        return [WarningEvidence(**dict(row)) for row in rows]

    def create_warning_evidence_from_data(self, data: dict[str, Any]) -> int:
        evidence_text = str(data.get("evidence_text", data.get("evidence", ""))).strip()
        if not evidence_text:
            raise ValueError("Warning evidence text is required")
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO warning_evidence(warning_id, evidence_text, source) VALUES (?, ?, ?)",
                (int(data.get("warning_id", 1) or 1), evidence_text, data.get("source", "Manual evidence")),
            )
            conn.execute("INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)", ("Eng. Ola", "create", "warning_evidence", cur.lastrowid))
            return int(cur.lastrowid)

    def meetings(self) -> list[Meeting]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id, title, meeting_type, meeting_date, status FROM meetings ORDER BY meeting_date").fetchall()
        return [Meeting(**dict(row)) for row in rows]

    def create_meeting(self, title: str, meeting_type: str, meeting_date: str, notes: str = "") -> int:
        if not title.strip():
            raise ValueError("Meeting title is required")
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO meetings(title, meeting_type, meeting_date, notes) VALUES (?, ?, ?, ?)",
                (title, meeting_type, meeting_date, notes),
            )
            conn.execute("INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)", ("Eng. Ola", "create", "meeting", cur.lastrowid))
            return int(cur.lastrowid)

    def create_meeting_from_data(self, data: dict[str, Any]) -> int:
        return self.create_meeting(
            str(data.get("title", "")).strip(),
            data.get("meeting_type", "PMO review"),
            data.get("meeting_date", date.today().isoformat()),
            data.get("notes", ""),
        )

    def attendees(self) -> list[Attendee]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id, meeting_id, name, role FROM attendees ORDER BY meeting_id, name").fetchall()
        return [Attendee(**dict(row)) for row in rows]

    def create_attendee_from_data(self, data: dict[str, Any]) -> int:
        name = str(data.get("name", "")).strip()
        if not name:
            raise ValueError("Attendee name is required")
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO attendees(meeting_id, name, role) VALUES (?, ?, ?)",
                (int(data.get("meeting_id", 1) or 1), name, data.get("role", "")),
            )
            conn.execute("INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)", ("Eng. Ola", "create", "attendee", cur.lastrowid))
            return int(cur.lastrowid)

    def agenda_items(self) -> list[AgendaItem]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id, meeting_id, title, related_warning_id, status FROM agenda_items ORDER BY meeting_id, id").fetchall()
        return [AgendaItem(**dict(row)) for row in rows]

    def create_agenda_item_from_data(self, data: dict[str, Any]) -> int:
        title = str(data.get("title", "")).strip()
        if not title:
            raise ValueError("Agenda item title is required")
        warning_id = data.get("related_warning_id", "")
        related_warning_id = int(warning_id) if str(warning_id).strip() else None
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO agenda_items(meeting_id, title, related_warning_id, status) VALUES (?, ?, ?, ?)",
                (int(data.get("meeting_id", 1) or 1), title, related_warning_id, data.get("status", "Open")),
            )
            conn.execute("INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)", ("Eng. Ola", "create", "agenda_item", cur.lastrowid))
            return int(cur.lastrowid)

    def save_reviewed_meeting_extraction(self, title: str, meeting_type: str, transcript: str, extracted: dict[str, str]) -> dict[str, int]:
        required = ["discussion_summary", "decision", "action_required", "responsible_person", "due_date", "priority", "related_project"]
        missing = [key for key in required if not str(extracted.get(key, "")).strip()]
        if missing:
            raise ValueError(f"Missing reviewed extraction fields: {', '.join(missing)}")
        meeting_title = title.strip() or "Executive meeting"
        meeting_notes = "\n\n".join(
            value
            for value in [
                transcript.strip(),
                extracted.get("meeting_minutes", "").strip(),
                extracted.get("follow_up_email_draft", "").strip(),
            ]
            if value
        )
        with self._conn() as conn:
            meeting = conn.execute(
                """
                INSERT INTO meetings(title, meeting_type, meeting_date, status, notes)
                VALUES (?, ?, ?, 'Documented', ?)
                """,
                (meeting_title, meeting_type or "Executive meeting", date.today().isoformat(), meeting_notes),
            )
            meeting_id = int(meeting.lastrowid)
            commitment = conn.execute(
                """
                INSERT INTO commitments(
                    title, description, owner, delegator, project, sector, priority,
                    due_date, status, progress, evidence, comments, escalation_level, audit_history
                ) VALUES (?, ?, ?, 'Eng. Ola', ?, 'Buildings', ?, ?, 'Open', 0, ?, ?, 0, ?)
                """,
                (
                    extracted["action_required"],
                    extracted["discussion_summary"],
                    extracted["responsible_person"],
                    extracted["related_project"],
                    extracted["priority"],
                    extracted["due_date"],
                    extracted.get("supporting_attachment", ""),
                    extracted.get("related_warning", ""),
                    f"Generated from reviewed extraction for meeting #{meeting_id}",
                ),
            )
            decision = conn.execute(
                """
                INSERT INTO decisions(title, project, status, due_date, source_meeting_id)
                VALUES (?, ?, 'Pending', ?, ?)
                """,
                (extracted["decision"], extracted["related_project"], extracted["due_date"], meeting_id),
            )
            agenda_lines = [
                line.strip(" -\t")
                for line in extracted.get("next_meeting_agenda", "").splitlines()
                if line.strip()
            ]
            for agenda_line in agenda_lines:
                conn.execute(
                    "INSERT INTO agenda_items(meeting_id, title, status) VALUES (?, ?, 'Open')",
                    (meeting_id, agenda_line),
                )
            attachment_ref = extracted.get("supporting_attachment", "").strip()
            if attachment_ref and not attachment_ref.lower().startswith("no attachment"):
                conn.execute(
                    "INSERT INTO attachments(entity_type, entity_id, file_name, file_path) VALUES ('meeting', ?, ?, ?)",
                    (meeting_id, Path(attachment_ref).name, attachment_ref),
                )
            conn.execute("INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)", ("Eng. Ola", "save-reviewed-extraction", "meeting", meeting_id))
            return {"meeting_id": meeting_id, "commitment_id": int(commitment.lastrowid), "decision_id": int(decision.lastrowid)}

    def commitments(self) -> list[Commitment]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id, title, owner, due_date, status, priority, project FROM commitments ORDER BY due_date").fetchall()
        return [Commitment(**dict(row)) for row in rows]

    def create_commitment(self, title: str, owner: str, due_date: str, project: str = "Configured PMO Project", priority: str = "High") -> int:
        if not title.strip() or not owner.strip():
            raise ValueError("Commitment title and owner are required")
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO commitments(title, owner, delegator, project, sector, priority, due_date, status)
                VALUES (?, ?, 'Eng. Ola', ?, 'Buildings', ?, ?, 'Open')
                """,
                (title, owner, project, priority or "High", due_date),
            )
            return int(cur.lastrowid)

    def create_commitment_from_data(self, data: dict[str, Any]) -> int:
        required = ["title", "owner", "due_date"]
        missing = [key for key in required if not str(data.get(key, "")).strip()]
        if missing:
            raise ValueError(f"Missing commitment fields: {', '.join(missing)}")
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO commitments(
                    title, description, owner, delegator, project, sector, priority,
                    due_date, status, progress, evidence, comments, escalation_level, audit_history
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["title"],
                    data.get("description", ""),
                    data["owner"],
                    data.get("delegator", "Eng. Ola"),
                    data.get("project", "Configured PMO Project"),
                    data.get("sector", "Buildings"),
                    data.get("priority", "High"),
                    data["due_date"],
                    data.get("status", "Open"),
                    int(data.get("progress", 0) or 0),
                    data.get("evidence", ""),
                    data.get("comments", ""),
                    int(data.get("escalation_level", 0) or 0),
                    data.get("audit_history", "Imported or manually entered"),
                ),
            )
            return int(cur.lastrowid)

    def update_commitment_status(self, commitment_id: int, status: str, progress: int | None = None) -> None:
        with self._conn() as conn:
            if progress is None:
                conn.execute("UPDATE commitments SET status = ? WHERE id = ?", (status, commitment_id))
            else:
                conn.execute("UPDATE commitments SET status = ?, progress = ? WHERE id = ?", (status, progress, commitment_id))
            conn.execute(
                "INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)",
                ("Eng. Ola", f"status:{status}", "commitment", commitment_id),
            )

    def update_commitment_core(self, commitment_id: int, title: str, owner: str, due_date: str, priority: str) -> None:
        if not title.strip() or not owner.strip() or not due_date.strip():
            raise ValueError("Commitment title, owner, and due date are required")
        with self._conn() as conn:
            conn.execute(
                "UPDATE commitments SET title = ?, owner = ?, due_date = ?, priority = ? WHERE id = ?",
                (title, owner, due_date, priority or "High", commitment_id),
            )
            conn.execute("INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)", ("Eng. Ola", "edit", "commitment", commitment_id))

    def decisions(self) -> list[Decision]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id, title, project, status, due_date FROM decisions ORDER BY due_date").fetchall()
        return [Decision(**dict(row)) for row in rows]

    def decision_audit(self, search: str = "") -> list[dict[str, str]]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT decisions.id, decisions.title, decisions.project, decisions.status, decisions.due_date,
                       decisions.created_at, meetings.title AS meeting_title, meetings.meeting_date
                FROM decisions
                LEFT JOIN meetings ON meetings.id = decisions.source_meeting_id
                WHERE ? = '' OR decisions.title LIKE ? OR decisions.project LIKE ? OR COALESCE(meetings.title, '') LIKE ?
                ORDER BY decisions.created_at DESC, decisions.id DESC
                """,
                (search, f"%{search}%", f"%{search}%", f"%{search}%"),
            ).fetchall()
        return [
            {
                "id": str(row["id"]),
                "title": str(row["title"]),
                "project": str(row["project"]),
                "status": str(row["status"]),
                "due_date": str(row["due_date"]),
                "created_at": str(row["created_at"]),
                "meeting_title": str(row["meeting_title"] or "No linked meeting"),
                "meeting_date": str(row["meeting_date"] or ""),
            }
            for row in rows
        ]

    def create_decision(self, title: str, project: str, due_date: str) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO decisions(title, project, status, due_date) VALUES (?, ?, 'Pending', ?)",
                (title, project, due_date),
            )
            return int(cur.lastrowid)

    def create_decision_from_data(self, data: dict[str, Any]) -> int:
        if not str(data.get("title", "")).strip():
            raise ValueError("Decision title is required")
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO decisions(title, project, status, due_date) VALUES (?, ?, ?, ?)",
                (
                    data["title"],
                    data.get("project", "Configured PMO Project"),
                    data.get("status", "Pending"),
                    data.get("due_date", date.today().isoformat()),
                ),
            )
            return int(cur.lastrowid)

    def update_decision_status(self, decision_id: int, status: str) -> None:
        with self._conn() as conn:
            conn.execute("UPDATE decisions SET status = ? WHERE id = ?", (status, decision_id))
            conn.execute(
                "INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)",
                ("Eng. Ola", f"status:{status}", "decision", decision_id),
            )

    def update_decision_core(self, decision_id: int, title: str, project: str, due_date: str) -> None:
        if not title.strip():
            raise ValueError("Decision title is required")
        with self._conn() as conn:
            conn.execute(
                "UPDATE decisions SET title = ?, project = ?, due_date = ? WHERE id = ?",
                (title, project or "Configured PMO Project", due_date or date.today().isoformat(), decision_id),
            )
            conn.execute("INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)", ("Eng. Ola", "edit", "decision", decision_id))

    def milestones(self) -> list[Milestone]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT milestones.id, milestones.title, projects.name AS project, milestones.due_date, milestones.status
                FROM milestones
                LEFT JOIN projects ON projects.id = milestones.project_id
                ORDER BY milestones.due_date
                """
            ).fetchall()
        return [Milestone(**dict(row)) for row in rows]

    def create_milestone_from_data(self, data: dict[str, Any]) -> int:
        if not str(data.get("title", "")).strip():
            raise ValueError("Milestone title is required")
        project_name = data.get("project", "Configured PMO Project")
        with self._conn() as conn:
            project = conn.execute("SELECT id FROM projects WHERE name = ?", (project_name,)).fetchone()
            project_id = int(project["id"]) if project else 1
            cur = conn.execute(
                "INSERT INTO milestones(project_id, title, due_date, status) VALUES (?, ?, ?, ?)",
                (project_id, data["title"], data.get("due_date", date.today().isoformat()), data.get("status", "Open")),
            )
            return int(cur.lastrowid)

    def update_milestone_status(self, milestone_id: int, status: str) -> None:
        with self._conn() as conn:
            conn.execute("UPDATE milestones SET status = ? WHERE id = ?", (status, milestone_id))
            conn.execute("INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)", ("Eng. Ola", f"status:{status}", "milestone", milestone_id))

    def comments(self) -> list[Comment]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id, entity_type, entity_id, author, body, created_at FROM comments ORDER BY created_at DESC").fetchall()
        return [Comment(**dict(row)) for row in rows]

    def create_comment_from_data(self, data: dict[str, Any]) -> int:
        body = str(data.get("body", data.get("comment", ""))).strip()
        if not body:
            raise ValueError("Comment body is required")
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO comments(entity_type, entity_id, author, body) VALUES (?, ?, ?, ?)",
                (
                    data.get("entity_type", "project"),
                    int(data.get("entity_id", 1) or 1),
                    data.get("author", "Eng. Ola"),
                    body,
                ),
            )
            conn.execute("INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)", ("Eng. Ola", "create", "comment", cur.lastrowid))
            return int(cur.lastrowid)

    def attachments(self) -> list[Attachment]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id, entity_type, entity_id, file_name, file_path, uploaded_at FROM attachments ORDER BY uploaded_at DESC").fetchall()
        return [Attachment(**dict(row)) for row in rows]

    def create_attachment_from_data(self, data: dict[str, Any]) -> int:
        file_path = str(data.get("file_path", data.get("path", ""))).strip()
        if not file_path:
            raise ValueError("Attachment file path is required")
        file_name = str(data.get("file_name", "")).strip() or Path(file_path).name
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO attachments(entity_type, entity_id, file_name, file_path) VALUES (?, ?, ?, ?)",
                (
                    data.get("entity_type", "project"),
                    int(data.get("entity_id", 1) or 1),
                    file_name,
                    file_path,
                ),
            )
            conn.execute("INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)", ("Eng. Ola", "create", "attachment", cur.lastrowid))
            return int(cur.lastrowid)

    def project_updates(self) -> list[ProjectUpdate]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT id, project, sector, update_date, progress, summary, next_milestone, issues, source
                FROM project_updates
                ORDER BY update_date DESC, id DESC
                """
            ).fetchall()
        return [ProjectUpdate(**dict(row)) for row in rows]

    def create_project_update(self, data: dict[str, Any]) -> int:
        required = ["project", "sector", "update_date", "summary"]
        missing = [key for key in required if not str(data.get(key, "")).strip()]
        if missing:
            raise ValueError(f"Missing project update fields: {', '.join(missing)}")
        progress = max(0, min(100, int(data.get("progress", 0) or 0)))
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO project_updates(project, sector, update_date, progress, summary, next_milestone, issues, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["project"],
                    data["sector"],
                    data["update_date"],
                    progress,
                    data["summary"],
                    data.get("next_milestone", ""),
                    data.get("issues", ""),
                    data.get("source", "Manual PMO update"),
                ),
            )
            conn.execute("INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)", ("Eng. Ola", "create", "project_update", cur.lastrowid))
            return int(cur.lastrowid)

    def private_tasks(self) -> list[PersonalTask]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id, title, category, due_date, status, is_private FROM personal_tasks WHERE is_private = 1 ORDER BY due_date").fetchall()
        return [PersonalTask(**dict(row)) for row in rows]

    def create_private_task(self, title: str, category: str, due_date: str) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO personal_tasks(title, category, due_date, is_private) VALUES (?, ?, ?, 1)",
                (title, category, due_date),
            )
            return int(cur.lastrowid)

    def create_private_task_from_data(self, data: dict[str, Any]) -> int:
        title = str(data.get("title", "")).strip()
        if not title:
            raise ValueError("Private task title is required")
        return self.create_private_task(title, data.get("category", "Priority"), data.get("due_date", date.today().isoformat()))

    def update_private_task_status(self, task_id: int, status: str) -> None:
        with self._conn() as conn:
            conn.execute("UPDATE personal_tasks SET status = ? WHERE id = ? AND is_private = 1", (status, task_id))

    def update_private_task_core(self, task_id: int, title: str, category: str, due_date: str) -> None:
        if not title.strip():
            raise ValueError("Private task title is required")
        with self._conn() as conn:
            conn.execute(
                "UPDATE personal_tasks SET title = ?, category = ?, due_date = ? WHERE id = ? AND is_private = 1",
                (title, category or "Priority", due_date or date.today().isoformat(), task_id),
            )

    def personal_events(self) -> list[PersonalEvent]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, title, event_date, category, is_private FROM personal_events WHERE is_private = 1 ORDER BY event_date"
            ).fetchall()
        return [PersonalEvent(**dict(row)) for row in rows]

    def create_personal_event(self, title: str, event_date: str, category: str) -> int:
        if not title.strip():
            raise ValueError("Personal event title is required")
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO personal_events(title, event_date, category, is_private) VALUES (?, ?, ?, 1)",
                (title, event_date or date.today().isoformat(), category or "Personal"),
            )
            return int(cur.lastrowid)

    def create_personal_event_from_data(self, data: dict[str, Any]) -> int:
        return self.create_personal_event(
            str(data.get("title", "")).strip(),
            data.get("event_date", data.get("due_date", date.today().isoformat())),
            data.get("category", "Personal"),
        )

    def private_notes(self) -> list[PrivateNote]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, title, body, is_private, created_at FROM private_notes WHERE is_private = 1 ORDER BY created_at DESC"
            ).fetchall()
        return [PrivateNote(**dict(row)) for row in rows]

    def create_private_note(self, title: str, body: str) -> int:
        if not title.strip():
            raise ValueError("Private note title is required")
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO private_notes(title, body, is_private) VALUES (?, ?, 1)",
                (title, body or ""),
            )
            return int(cur.lastrowid)

    def create_private_note_from_data(self, data: dict[str, Any]) -> int:
        return self.create_private_note(str(data.get("title", "")).strip(), data.get("body", data.get("note", "")))

    def wellbeing_checkins(self) -> list[WellbeingCheckin]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, checkin_date, water, break_done, stress_level, is_private FROM wellbeing_checkins WHERE is_private = 1 ORDER BY checkin_date DESC"
            ).fetchall()
        return [WellbeingCheckin(**dict(row)) for row in rows]

    def create_wellbeing_checkin(self, checkin_date: str, water: int, break_done: int, stress_level: int) -> int:
        stress = max(1, min(5, int(stress_level or 3)))
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO wellbeing_checkins(checkin_date, water, break_done, stress_level, is_private) VALUES (?, ?, ?, ?, 1)",
                (checkin_date or date.today().isoformat(), int(bool(water)), int(bool(break_done)), stress),
            )
            return int(cur.lastrowid)

    def create_wellbeing_checkin_from_data(self, data: dict[str, Any]) -> int:
        return self.create_wellbeing_checkin(
            data.get("checkin_date", date.today().isoformat()),
            int(str(data.get("water", "0") or "0")),
            int(str(data.get("break_done", "0") or "0")),
            int(str(data.get("stress_level", "3") or "3")),
        )

    def delete_record(self, entity_type: str, entity_id: int) -> None:
        tables = {
            "warning": "warnings",
            "meeting": "meetings",
            "commitment": "commitments",
            "decision": "decisions",
            "milestone": "milestones",
            "project": "projects",
            "project_update": "project_updates",
            "comment": "comments",
            "attachment": "attachments",
            "warning_evidence": "warning_evidence",
            "attendee": "attendees",
            "agenda_item": "agenda_items",
            "private_task": "personal_tasks",
            "personal_event": "personal_events",
            "private_note": "private_notes",
            "wellbeing_checkin": "wellbeing_checkins",
        }
        if entity_type not in tables:
            raise ValueError(f"Unsupported entity type: {entity_type}")
        with self._conn() as conn:
            if entity_type == "warning":
                conn.execute("DELETE FROM warning_evidence WHERE warning_id = ?", (entity_id,))
                conn.execute("DELETE FROM agenda_items WHERE related_warning_id = ?", (entity_id,))
            if entity_type == "meeting":
                conn.execute("DELETE FROM attendees WHERE meeting_id = ?", (entity_id,))
                conn.execute("DELETE FROM agenda_items WHERE meeting_id = ?", (entity_id,))
            conn.execute(f"DELETE FROM {tables[entity_type]} WHERE id = ?", (entity_id,))
            conn.execute("INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)", ("Eng. Ola", "delete", entity_type, entity_id))

    def notifications(self) -> list[sqlite3.Row]:
        with self._conn() as conn:
            return conn.execute("SELECT * FROM notifications ORDER BY created_at DESC").fetchall()

    def create_notification_delivery(self, channel: str, recipient: str, subject: str, body: str, status: str, provider_response: str) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO notification_deliveries(channel, recipient, subject, body, status, provider_response)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (channel, recipient, subject, body, status, provider_response),
            )
            conn.execute("INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)", ("Eng. Ola", f"notify:{channel}:{status}", "notification_delivery", cur.lastrowid))
            return int(cur.lastrowid)

    def notification_deliveries(self, limit: int = 20) -> list[dict[str, str]]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT channel, recipient, subject, status, provider_response, created_at
                FROM notification_deliveries
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def create_calendar_event(self, external_id: str, title: str, start_time: str, end_time: str, source: str) -> int:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO calendar_events(external_id, title, start_time, end_time, source)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(external_id) DO UPDATE SET title=excluded.title, start_time=excluded.start_time, end_time=excluded.end_time, source=excluded.source
                """,
                (external_id, title, start_time, end_time, source),
            )
            row = conn.execute("SELECT id FROM calendar_events WHERE external_id = ?", (external_id,)).fetchone()
            return int(row["id"])

    def calendar_events(self, limit: int = 20) -> list[dict[str, str]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT title, start_time, end_time, source FROM calendar_events ORDER BY start_time LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def create_voice_capture(self, scope: str, source_path: str, transcript: str, routed_to: str = "") -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO voice_captures(scope, source_path, transcript, routed_to) VALUES (?, ?, ?, ?)",
                (scope, source_path, transcript, routed_to),
            )
            conn.execute("INSERT INTO audit_logs(actor, action, entity_type, entity_id) VALUES (?, ?, ?, ?)", ("Eng. Ola", "voice-capture", scope, cur.lastrowid))
            return int(cur.lastrowid)

    def voice_captures(self, scope: str = "") -> list[dict[str, str]]:
        query = "SELECT id, scope, source_path, transcript, routed_to, created_at FROM voice_captures"
        params: list[Any] = []
        if scope:
            query += " WHERE scope = ?"
            params.append(scope)
        query += " ORDER BY created_at DESC, id DESC"
        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def audit_logs(self, limit: int = 20) -> list[dict[str, str]]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT actor, action, entity_type, entity_id, created_at
                FROM audit_logs
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "actor": str(row["actor"]),
                "action": str(row["action"]),
                "entity_type": str(row["entity_type"]),
                "entity_id": "" if row["entity_id"] is None else str(row["entity_id"]),
                "created_at": str(row["created_at"]),
            }
            for row in rows
        ]

    def ai_records_context(self, include_private: bool = False) -> dict[str, Any]:
        context: dict[str, Any] = {
            "warnings": [w.__dict__ for w in self.warnings()],
            "commitments": [c.__dict__ for c in self.commitments()],
            "decisions": [d.__dict__ for d in self.decisions()],
            "meetings": [m.__dict__ for m in self.meetings()],
            "warning_evidence": [e.__dict__ for e in self.warning_evidence()],
            "attendees": [a.__dict__ for a in self.attendees()],
            "agenda_items": [a.__dict__ for a in self.agenda_items()],
            "projects": [p.__dict__ for p in self.projects()],
            "project_updates": [p.__dict__ for p in self.project_updates()],
            "comments": [c.__dict__ for c in self.comments()],
            "attachments": [a.__dict__ for a in self.attachments()],
        }
        if include_private:
            context["private_tasks"] = [t.__dict__ for t in self.private_tasks()]
            context["personal_events"] = [e.__dict__ for e in self.personal_events()]
            context["private_notes"] = [n.__dict__ for n in self.private_notes()]
            context["wellbeing_checkins"] = [w.__dict__ for w in self.wellbeing_checkins()]
        return context

    def import_csv_preview(self, path: Path, limit: int = 20) -> list[dict[str, str]]:
        if path.suffix.lower() != ".csv":
            raise ValueError("Only CSV preview is supported by this local validator")
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return list(csv.DictReader(handle))[:limit]
