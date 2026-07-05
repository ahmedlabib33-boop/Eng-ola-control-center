# Database Schema

SQLite tables include:

- users, roles
- sectors, projects, project_updates, milestones
- warnings, warning_evidence
- meetings, attendees, agenda_items
- decisions, commitments
- comments, attachments
- notifications
- ai_conversations
- personal_tasks, personal_events, private_notes, wellbeing_checkins
- audit_logs

Repository boundaries are concentrated in `ola_360/repositories/` so the database can later migrate to PostgreSQL or Supabase.
