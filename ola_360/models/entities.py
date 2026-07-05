from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    name: str
    email: str
    role: str


@dataclass(frozen=True)
class WarningItem:
    id: int
    title: str
    category: str
    sector: str
    project: str
    severity: str
    trend: str
    owner: str
    date_identified: str
    due_date: str
    evidence: str
    potential_impact: str
    impacted_milestone: str
    recommended_intervention: str
    source: str
    last_update: str
    status: str


@dataclass(frozen=True)
class WarningEvidence:
    id: int
    warning_id: int
    evidence_text: str
    source: str
    created_at: str


@dataclass(frozen=True)
class Meeting:
    id: int
    title: str
    meeting_type: str
    meeting_date: str
    status: str


@dataclass(frozen=True)
class Attendee:
    id: int
    meeting_id: int
    name: str
    role: str


@dataclass(frozen=True)
class AgendaItem:
    id: int
    meeting_id: int
    title: str
    related_warning_id: int | None
    status: str


@dataclass(frozen=True)
class Commitment:
    id: int
    title: str
    owner: str
    due_date: str
    status: str
    priority: str
    project: str


@dataclass(frozen=True)
class Decision:
    id: int
    title: str
    project: str
    status: str
    due_date: str


@dataclass(frozen=True)
class Milestone:
    id: int
    title: str
    project: str
    due_date: str
    status: str


@dataclass(frozen=True)
class Project:
    id: int
    name: str
    sector: str
    status: str


@dataclass(frozen=True)
class ProjectUpdate:
    id: int
    project: str
    sector: str
    update_date: str
    progress: int
    summary: str
    next_milestone: str
    issues: str
    source: str


@dataclass(frozen=True)
class PersonalTask:
    id: int
    title: str
    category: str
    due_date: str
    status: str = "Open"
    is_private: int = 1


@dataclass(frozen=True)
class PersonalEvent:
    id: int
    title: str
    event_date: str
    category: str
    is_private: int = 1


@dataclass(frozen=True)
class PrivateNote:
    id: int
    title: str
    body: str
    is_private: int = 1
    created_at: str = ""


@dataclass(frozen=True)
class WellbeingCheckin:
    id: int
    checkin_date: str
    water: int
    break_done: int
    stress_level: int
    is_private: int = 1


@dataclass(frozen=True)
class Comment:
    id: int
    entity_type: str
    entity_id: int
    author: str
    body: str
    created_at: str


@dataclass(frozen=True)
class Attachment:
    id: int
    entity_type: str
    entity_id: int
    file_name: str
    file_path: str
    uploaded_at: str
