# OLA 360

**OLA 360 | Executive PMO Chief of Staff** is a mobile-first Flet application for secure morning briefings, early warnings, meetings, commitments, safe AI assistance, and private personal productivity.

## Run Locally

```powershell
cd "D:\Eng. OLA"
.\INSTALL_AND_RUN.ps1
```

Login is currently disabled for the local working build. The app opens directly as Eng. Ola.

Seeded credentials are still preserved for when login is restored:

- Email: `ola@samco.local`
- Password: `Ola360!`

## Run Modes

- Web: `.\RUN_FLET_WEB.ps1`
- Desktop: `.\RUN_FLET_DESKTOP.ps1`
- Main launcher: `.\RUN_APP.bat`
- Tests: `.\RUN_TESTS.ps1`

The database is stored at `data/ola_360.db` and is not deleted by build/clean scripts.

## Data Input Templates

Templates are in `templates/`.

- `warnings_template.csv` and `critical_issues_template.csv` import through Radar.
- `warning_evidence_template.csv` supports evidence rows linked to warnings.
- `meetings_template.csv`, `attendees_template.csv`, and `agenda_items_template.csv` support meeting setup and agenda preparation.
- `commitments_template.csv`, `decisions_template.csv`, and `milestones_template.csv` import through Meetings.
- `personal_tasks_template.csv` imports through My Day - Private.
- `meeting_notes_template.txt` can be pasted into the Meetings recording/transcript box before extraction.

CSV and XLSX files are supported when the headers match the templates. Exports are written to `exports/`. Imported and AI-extracted actions remain reviewable before management use.

Executive PMO reports can be generated from Home. The report is written to `exports/` as Markdown and uses PMO records only; My Day private records are excluded.

## Old Program

The previous Streamlit version and other non-main folders are archived in:

```text
D:\Eng. OLA\OLD PROGRAM
```
