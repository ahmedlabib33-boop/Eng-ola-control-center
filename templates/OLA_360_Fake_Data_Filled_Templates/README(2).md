# OLA 360 Templates

Use these files for structured data entry and imports. You can use the CSV files directly or copy the same headers into Excel and save as `.xlsx`.

- `warnings_template.csv`: early-warning radar records.
- `warning_evidence_template.csv`: supporting evidence rows linked to warning IDs.
- `critical_issues_template.csv`: critical issues imported as warnings.
- `projects_template.csv`: project master data and sector assignment.
- `meetings_template.csv`: meeting records.
- `attendees_template.csv`: meeting attendee records linked to meeting IDs.
- `agenda_items_template.csv`: agenda records linked to meeting IDs and optional warning IDs.
- `commitments_template.csv`: action register and commitment records.
- `decisions_template.csv`: decision register records.
- `milestones_template.csv`: milestone register records.
- `project_updates_template.csv`: PMO project progress updates used for data freshness and missing-update alerts.
- `comments_template.csv`: evidence, review notes, and management comments linked to an entity type/id.
- `attachments_template.csv`: supporting attachment references linked to an entity type/id.
- `personal_tasks_template.csv`: private My Day records.
- `personal_events_template.csv`: private appointments, family reminders, renewals, and important dates.
- `private_notes_template.csv`: private notes, ideas, reading lists, travel checklists, and shopping lists.
- `wellbeing_checkins_template.csv`: private wellbeing check-ins using non-medical water, break, and stress-level fields.
- `meeting_notes_template.txt`: paste into the Meetings recording/transcript box before extraction.

Keep column headers unchanged. Review imported or AI-extracted records before using them for management reporting. Exports are written to the app `exports/` folder.

Executive PMO reports are generated from the Home screen into `exports/` as Markdown files. They use stored PMO records only and intentionally exclude My Day private records.
