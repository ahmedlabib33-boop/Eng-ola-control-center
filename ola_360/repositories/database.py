from __future__ import annotations

import sqlite3
from pathlib import Path

from ola_360.core.security import hash_password


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    remember_device INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sectors (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    sector_id INTEGER REFERENCES sectors(id),
    status TEXT DEFAULT 'Active'
);

CREATE TABLE IF NOT EXISTS project_updates (
    id INTEGER PRIMARY KEY,
    project TEXT NOT NULL,
    sector TEXT NOT NULL,
    update_date TEXT NOT NULL,
    progress INTEGER DEFAULT 0,
    summary TEXT NOT NULL,
    next_milestone TEXT DEFAULT '',
    issues TEXT DEFAULT '',
    source TEXT DEFAULT 'Manual PMO update',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS milestones (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    title TEXT NOT NULL,
    due_date TEXT NOT NULL,
    status TEXT DEFAULT 'Open'
);

CREATE TABLE IF NOT EXISTS warnings (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    sector TEXT NOT NULL,
    project TEXT NOT NULL,
    severity TEXT NOT NULL,
    trend TEXT NOT NULL,
    evidence TEXT NOT NULL,
    potential_impact TEXT NOT NULL,
    impacted_milestone TEXT,
    owner TEXT NOT NULL,
    date_identified TEXT NOT NULL,
    due_date TEXT NOT NULL,
    recommended_intervention TEXT NOT NULL,
    source TEXT NOT NULL,
    last_update TEXT NOT NULL,
    status TEXT DEFAULT 'Open'
);

CREATE TABLE IF NOT EXISTS warning_evidence (
    id INTEGER PRIMARY KEY,
    warning_id INTEGER REFERENCES warnings(id),
    evidence_text TEXT NOT NULL,
    source TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS meetings (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    meeting_type TEXT NOT NULL,
    meeting_date TEXT NOT NULL,
    status TEXT DEFAULT 'Planned',
    notes TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS attendees (
    id INTEGER PRIMARY KEY,
    meeting_id INTEGER REFERENCES meetings(id),
    name TEXT NOT NULL,
    role TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS agenda_items (
    id INTEGER PRIMARY KEY,
    meeting_id INTEGER REFERENCES meetings(id),
    title TEXT NOT NULL,
    related_warning_id INTEGER,
    status TEXT DEFAULT 'Open'
);

CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    project TEXT NOT NULL,
    status TEXT NOT NULL,
    due_date TEXT NOT NULL,
    source_meeting_id INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS commitments (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    owner TEXT NOT NULL,
    delegator TEXT NOT NULL,
    project TEXT NOT NULL,
    sector TEXT NOT NULL,
    priority TEXT NOT NULL,
    due_date TEXT NOT NULL,
    status TEXT NOT NULL,
    progress INTEGER DEFAULT 0,
    evidence TEXT DEFAULT '',
    comments TEXT DEFAULT '',
    escalation_level INTEGER DEFAULT 0,
    audit_history TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    author TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    category TEXT NOT NULL,
    priority TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_conversations (
    id INTEGER PRIMARY KEY,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    sources TEXT DEFAULT '',
    confidence TEXT DEFAULT 'Medium',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS personal_tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    due_date TEXT NOT NULL,
    status TEXT DEFAULT 'Open',
    is_private INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS personal_events (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    event_date TEXT NOT NULL,
    category TEXT NOT NULL,
    is_private INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS private_notes (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    is_private INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS wellbeing_checkins (
    id INTEGER PRIMARY KEY,
    checkin_date TEXT NOT NULL,
    water INTEGER DEFAULT 0,
    break_done INTEGER DEFAULT 0,
    stress_level INTEGER DEFAULT 3,
    is_private INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)
        seed_db(conn)


def seed_db(conn: sqlite3.Connection) -> None:
    conn.execute("INSERT OR IGNORE INTO roles(name) VALUES ('Executive'), ('PMO Admin')")
    conn.execute(
        """
        INSERT OR IGNORE INTO users(id, name, email, password_hash, role)
        VALUES (1, 'Eng. Ola', 'ola@samco.local', ?, 'Executive')
        """,
        (hash_password("Ola360!"),),
    )
    for sector in ["Buildings", "Tunnels", "Infrastructure", "Roads", "Other"]:
        conn.execute("INSERT OR IGNORE INTO sectors(name) VALUES (?)", (sector,))
    conn.execute(
        """
        INSERT OR IGNORE INTO projects(id, name, sector_id, status)
        VALUES (1, 'Configured PMO Project', 1, 'Active')
        """
    )
    conn.execute(
        """
        INSERT OR IGNORE INTO project_updates(
            id, project, sector, update_date, progress, summary, next_milestone, issues, source
        ) VALUES (
            1, 'Configured PMO Project', 'Buildings', date('now', '-9 day'), 62,
            'Seed update is intentionally older than the freshness threshold.',
            'Next sector review milestone', 'Recovery-plan evidence still open.', 'Seed stored data'
        )
        """
    )
    conn.execute(
        """
        INSERT OR IGNORE INTO warnings(
            id, title, category, sector, project, severity, trend, evidence,
            potential_impact, impacted_milestone, owner, date_identified, due_date,
            recommended_intervention, source, last_update, status
        ) VALUES (
            1, 'Milestone recovery plan requires review', 'Schedule', 'Buildings',
            'Configured PMO Project', 'Critical', 'Deteriorating',
            'Latest stored update shows recovery action is not closed.',
            'May affect executive reporting and milestone confidence.',
            'Next sector review milestone', 'Project Manager', date('now', '-2 day'),
            date('now', '-1 day'), 'Request dated recovery plan and owner confirmation.',
            'Seed stored data', datetime('now'), 'Open'
        )
        """
    )
    conn.execute(
        """
        INSERT OR IGNORE INTO meetings(id, title, meeting_type, meeting_date, status, notes)
        VALUES (1, 'PMO Morning Review', 'PMO review', date('now'), 'Planned', 'Review open warnings and commitments.')
        """
    )
    conn.execute(
        """
        INSERT OR IGNORE INTO decisions(id, title, project, status, due_date)
        VALUES (1, 'Approve recovery-plan request', 'Configured PMO Project', 'Pending', date('now'))
        """
    )
    conn.execute(
        """
        INSERT OR IGNORE INTO commitments(
            id, title, description, owner, delegator, project, sector, priority,
            due_date, status, progress, audit_history
        ) VALUES (
            1, 'Submit recovery-plan evidence', 'Provide approved evidence and dated mitigation steps.',
            'Project Manager', 'Eng. Ola', 'Configured PMO Project', 'Buildings',
            'High', date('now', '-1 day'), 'Overdue', 40, 'Seeded local record'
        )
        """
    )
    conn.execute(
        """
        INSERT OR IGNORE INTO personal_tasks(id, title, category, due_date, status, is_private)
        VALUES (1, 'Confirm family appointment', 'Family', date('now'), 'Open', 1)
        """
    )
    conn.execute(
        """
        INSERT OR IGNORE INTO notifications(id, title, message, category, priority)
        VALUES (1, 'Critical warning requires review', 'One critical warning is overdue.', 'Warning', 'Critical')
        """
    )
