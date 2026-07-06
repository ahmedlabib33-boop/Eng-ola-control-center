from __future__ import annotations

from datetime import date
from pathlib import Path

import flet as ft

from ola_360.components.forms import dropdown, input_field
from ola_360.components.ui import card, chip, text
from ola_360.core.theme import PALETTE
from ola_360.repositories.app_repository import AppRepository
from ola_360.services.ai_service import AIService
from ola_360.services.export_service import ExportService
from ola_360.services.import_service import ImportService


def meetings_view(repo: AppRepository, ai: AIService, refresh) -> ft.Control:
    importer = ImportService(repo)
    exporter = ExportService(repo, repo.db_path.parents[1] / "exports")
    title = input_field("Meeting title")
    mtype = dropdown("Meeting type", ["PMO review", "Sector review", "Project progress meeting", "Executive meeting", "Recovery workshop", "Risk meeting", "Commercial meeting", "Personal meeting"])
    notes = ft.TextField(label="Verbatim transcript / pasted meeting notes", multiline=True, min_lines=8, border_radius=14)
    transcript_path = input_field("Transcript .txt path")
    attachment = input_field("Supporting attachment reference")
    commitment_import_path = input_field("Commitments CSV/XLSX path")
    decision_import_path = input_field("Decisions CSV/XLSX path")
    milestone_import_path = input_field("Milestones CSV/XLSX path")
    recording_state = ft.Text("Transcript mode is ready. Paste or import the complete transcript before extraction.", size=12, color=PALETTE.muted, no_wrap=False)
    import_status = ft.Text("", color=PALETTE.emerald, size=12, no_wrap=False)
    extracted = ft.Column(spacing=6)
    extracted_data: dict[str, str] = {}
    extracted_fields: dict[str, ft.TextField] = {}
    capture_state = {"active": False}

    def create_meeting(e):
        repo.create_meeting(title.value, mtype.value, date.today().isoformat(), notes.value)
        refresh()

    def toggle_recording(e):
        if not capture_state["active"]:
            capture_state["active"] = True
            recording_state.value = "Transcript capture is active. Type or paste every spoken word here; the app preserves this text verbatim."
            recording_state.color = PALETTE.amber
            e.control.text = "Stop transcript capture"
            e.control.icon = ft.Icons.STOP_CIRCLE_OUTLINED
        else:
            capture_state["active"] = False
            recording_state.value = "Transcript capture stopped. Review the verbatim transcript before extraction."
            recording_state.color = PALETTE.emerald
            e.control.text = "Start transcript capture"
            e.control.icon = ft.Icons.MIC
        e.page.update()

    def import_transcript(e):
        try:
            path = Path(transcript_path.value.strip())
            if not path.exists() or path.suffix.lower() != ".txt":
                raise ValueError("Enter a valid .txt transcript path.")
            notes.value = path.read_text(encoding="utf-8")
            recording_state.value = f"Transcript imported exactly from {path.name}. Review before extraction."
            recording_state.color = PALETTE.emerald
            e.page.update()
        except Exception as exc:
            recording_state.value = str(exc)
            recording_state.color = PALETTE.red
            e.page.update()

    def current_reviewed_extraction() -> dict[str, str]:
        reviewed = dict(extracted_data)
        for key, field in extracted_fields.items():
            reviewed[key] = field.value or ""
        return reviewed

    def output_box(label: str, value: str, lines: int = 2, key: str | None = None) -> ft.TextField:
        field = ft.TextField(label=label, value=value, multiline=True, min_lines=lines, border_radius=14)
        if key:
            extracted_fields[key] = field
        return field

    def extract(e):
        result = ai.extract_meeting_intelligence(notes.value or "", title.value or "Executive meeting")
        if attachment.value:
            result["supporting_attachment"] = attachment.value
        extracted_data.clear()
        extracted_data.update(result)
        extracted_fields.clear()
        extracted.controls = [
            text("Reviewed extraction draft. Nothing is saved or sent until Eng. Ola approves it.", 13, color=PALETTE.amber),
            card(
                [
                    output_box("Verbatim transcript preserved", result["verbatim_transcript"], 8, "verbatim_transcript"),
                    output_box("Extraction quality note", result["extraction_quality"], 2, "extraction_quality"),
                    output_box("Discussion summary in points", result["discussion_summary"], 5, "discussion_summary"),
                    output_box("Decision", result["decision"], key="decision"),
                    output_box("Action required", result["action_required"], key="action_required"),
                    output_box("Responsible person", result["responsible_person"], key="responsible_person"),
                    ft.Row([output_box("Due date", result["due_date"], key="due_date"), output_box("Priority", result["priority"], key="priority")], wrap=True),
                    output_box("Related project", result["related_project"], key="related_project"),
                    output_box("Related warning", result["related_warning"], key="related_warning"),
                    output_box("Supporting attachment", result["supporting_attachment"], key="supporting_attachment"),
                    ft.Row(
                        [
                            ft.ElevatedButton("Save all reviewed outputs", icon=ft.Icons.VERIFIED, on_click=save_reviewed_outputs),
                            ft.ElevatedButton("Save reviewed action", icon=ft.Icons.TASK_ALT, on_click=save_action),
                            ft.OutlinedButton("Save reviewed decision", icon=ft.Icons.GAVEL, on_click=save_decision),
                        ],
                        wrap=True,
                    ),
                ],
                accent=PALETTE.bronze,
            ),
            text("Auto-generated management outputs", 16, ft.FontWeight.BOLD),
            output_box("Meeting minutes", result["meeting_minutes"], 7, "meeting_minutes"),
            output_box("Action register", result["action_register"], 2, "action_register"),
            output_box("Decision register", result["decision_register"], 2, "decision_register"),
            output_box("Follow-up email draft", result["follow_up_email_draft"], 7, "follow_up_email_draft"),
            output_box("Next meeting agenda", result["next_meeting_agenda"], 4, "next_meeting_agenda"),
            output_box("Overdue-action list", result["overdue_action_list"], 4, "overdue_action_list"),
        ]
        e.page.update()

    def save_reviewed_outputs(e):
        if not extracted_data:
            return
        try:
            repo.save_reviewed_meeting_extraction(title.value, mtype.value, notes.value or "", current_reviewed_extraction())
            refresh()
        except Exception as exc:
            import_status.value = str(exc)
            import_status.color = PALETTE.red
            e.page.update()

    def save_action(e):
        if not extracted_data:
            return
        reviewed = current_reviewed_extraction()
        repo.create_commitment(
            reviewed["action_required"],
            reviewed["responsible_person"],
            reviewed["due_date"],
            reviewed["related_project"],
            reviewed["priority"],
        )
        refresh()

    def save_decision(e):
        if not extracted_data:
            return
        reviewed = current_reviewed_extraction()
        repo.create_decision(reviewed["decision"], reviewed["related_project"], reviewed["due_date"])
        refresh()

    def import_commitments(e):
        try:
            result = importer.import_file(commitment_import_path.value, "commitments")
            import_status.value = f"Imported {result['imported']} commitment row(s)."
            import_status.color = PALETTE.emerald if not result["errors"] else PALETTE.amber
            if result["errors"]:
                import_status.value += " Review: " + "; ".join(result["errors"][:3])
            refresh()
        except Exception as exc:
            import_status.value = str(exc)
            import_status.color = PALETTE.red
            e.page.update()

    def import_decisions(e):
        try:
            result = importer.import_file(decision_import_path.value, "decisions")
            import_status.value = f"Imported {result['imported']} decision row(s)."
            import_status.color = PALETTE.emerald if not result["errors"] else PALETTE.amber
            if result["errors"]:
                import_status.value += " Review: " + "; ".join(result["errors"][:3])
            refresh()
        except Exception as exc:
            import_status.value = str(exc)
            import_status.color = PALETTE.red
            e.page.update()

    def import_milestones(e):
        try:
            result = importer.import_file(milestone_import_path.value, "milestones")
            import_status.value = f"Imported {result['imported']} milestone row(s)."
            import_status.color = PALETTE.emerald if not result["errors"] else PALETTE.amber
            if result["errors"]:
                import_status.value += " Review: " + "; ".join(result["errors"][:3])
            refresh()
        except Exception as exc:
            import_status.value = str(exc)
            import_status.color = PALETTE.red
            e.page.update()

    def export_dataset(dataset: str, e):
        try:
            output = exporter.export(dataset)
            import_status.value = f"{dataset.replace('_', ' ').title()} exported: {output}"
            import_status.color = PALETTE.emerald
            e.page.update()
        except Exception as exc:
            import_status.value = str(exc)
            import_status.color = PALETTE.red
            e.page.update()

    meeting_cards = [
        card(
            [
                ft.Row([text(item.title, 16, ft.FontWeight.BOLD), chip(item.status, PALETTE.blue)], wrap=True),
                text(f"{item.meeting_type} | {item.meeting_date}", 12, color=PALETTE.muted),
                ft.OutlinedButton("Delete meeting", icon=ft.Icons.DELETE_OUTLINE, on_click=lambda e, item=item: repo.delete_record("meeting", item.id) or refresh()),
            ]
        )
        for item in repo.meetings()
    ]

    def commitment_card(item):
        edit_title = input_field("Edit commitment", item.title)
        edit_owner = input_field("Edit owner", item.owner)
        edit_due = input_field("Edit due date", item.due_date)
        edit_priority = input_field("Edit priority", item.priority)
        edit_status = ft.Text("", color=PALETTE.emerald, size=12, no_wrap=False)

        def save_edit(e):
            try:
                repo.update_commitment_core(item.id, edit_title.value, edit_owner.value, edit_due.value, edit_priority.value)
                refresh()
            except Exception as exc:
                edit_status.value = str(exc)
                edit_status.color = PALETTE.red
                e.page.update()

        return card(
            [
                ft.Row([text(item.title, 15, ft.FontWeight.BOLD), chip(item.status, PALETTE.amber)], wrap=True),
                text(f"Owner: {item.owner} | Due: {item.due_date}", 12, color=PALETTE.muted),
                ft.Row(
                    [
                        ft.OutlinedButton("Complete", icon=ft.Icons.CHECK, on_click=lambda e, item=item: repo.update_commitment_status(item.id, "Completed", 100) or refresh()),
                        ft.OutlinedButton("Escalate", icon=ft.Icons.PRIORITY_HIGH, on_click=lambda e, item=item: repo.update_commitment_status(item.id, "Escalated") or refresh()),
                        ft.OutlinedButton("Delete", icon=ft.Icons.DELETE_OUTLINE, on_click=lambda e, item=item: repo.delete_record("commitment", item.id) or refresh()),
                    ],
                    wrap=True,
                ),
                ft.ExpansionTile(
                    title=text("Edit commitment", 13, ft.FontWeight.BOLD),
                    controls=[edit_title, edit_owner, edit_due, edit_priority, ft.OutlinedButton("Save correction", icon=ft.Icons.SAVE, on_click=save_edit), edit_status],
                ),
            ]
        )

    commitment_cards = [commitment_card(item) for item in repo.commitments()]

    def decision_card(item):
        edit_title = input_field("Edit decision", item.title)
        edit_project = input_field("Edit project", item.project)
        edit_due = input_field("Edit due date", item.due_date)
        edit_status = ft.Text("", color=PALETTE.emerald, size=12, no_wrap=False)

        def save_edit(e):
            try:
                repo.update_decision_core(item.id, edit_title.value, edit_project.value, edit_due.value)
                refresh()
            except Exception as exc:
                edit_status.value = str(exc)
                edit_status.color = PALETTE.red
                e.page.update()

        return card(
            [
                ft.Row([text(item.title, 15, ft.FontWeight.BOLD), chip(item.status, PALETTE.blue)], wrap=True),
                text(f"{item.project} | Due: {item.due_date}", 12, color=PALETTE.muted),
                ft.Row(
                    [
                        ft.OutlinedButton("Approve", icon=ft.Icons.THUMB_UP_OUTLINED, on_click=lambda e, item=item: repo.update_decision_status(item.id, "Approved") or refresh()),
                        ft.OutlinedButton("Defer", icon=ft.Icons.SCHEDULE, on_click=lambda e, item=item: repo.update_decision_status(item.id, "Deferred") or refresh()),
                        ft.OutlinedButton("Delete", icon=ft.Icons.DELETE_OUTLINE, on_click=lambda e, item=item: repo.delete_record("decision", item.id) or refresh()),
                    ],
                    wrap=True,
                ),
                ft.ExpansionTile(
                    title=text("Edit decision", 13, ft.FontWeight.BOLD),
                    controls=[edit_title, edit_project, edit_due, ft.OutlinedButton("Save correction", icon=ft.Icons.SAVE, on_click=save_edit), edit_status],
                ),
            ]
        )

    decision_cards = [decision_card(item) for item in repo.decisions()]

    milestone_cards = [
        card(
            [
                ft.Row([text(item.title, 15, ft.FontWeight.BOLD), chip(item.status, PALETTE.emerald)], wrap=True),
                text(f"{item.project} | Due: {item.due_date}", 12, color=PALETTE.muted),
                ft.Row(
                    [
                        ft.OutlinedButton("Complete", icon=ft.Icons.CHECK, on_click=lambda e, item=item: repo.update_milestone_status(item.id, "Completed") or refresh()),
                        ft.OutlinedButton("Delete", icon=ft.Icons.DELETE_OUTLINE, on_click=lambda e, item=item: repo.delete_record("milestone", item.id) or refresh()),
                    ],
                    wrap=True,
                ),
            ]
        )
        for item in repo.milestones()
    ]
    return ft.ListView(
        expand=True,
        spacing=12,
        controls=[
            text("Meetings, Decisions, Commitments", 23, ft.FontWeight.BOLD),
            ft.ExpansionTile(
                title=text("Recording and auto-extraction center", 16, ft.FontWeight.BOLD),
                controls=[
                    title,
                    mtype,
                    ft.Row(
                        [
                            ft.ElevatedButton("Start transcript capture", icon=ft.Icons.MIC, on_click=toggle_recording),
                            ft.OutlinedButton("Import .txt transcript", icon=ft.Icons.UPLOAD_FILE, on_click=import_transcript),
                            ft.OutlinedButton("Create meeting", icon=ft.Icons.EVENT_NOTE, on_click=create_meeting),
                            ft.OutlinedButton("Extract and generate", icon=ft.Icons.AUTO_AWESOME, on_click=extract),
                        ],
                        wrap=True,
                    ),
                    recording_state,
                    transcript_path,
                    notes,
                    attachment,
                    extracted,
                ],
            ),
            ft.ExpansionTile(
                title=text("Import registers from templates", 16, ft.FontWeight.BOLD),
                controls=[
                    text("Use the CSV templates directly, or save the same headers as XLSX. Imported rows are stored in local SQLite.", 12, color=PALETTE.muted),
                    commitment_import_path,
                    ft.ElevatedButton("Import commitments", icon=ft.Icons.UPLOAD_FILE, on_click=import_commitments),
                    decision_import_path,
                    ft.OutlinedButton("Import decisions", icon=ft.Icons.UPLOAD_FILE, on_click=import_decisions),
                    milestone_import_path,
                    ft.OutlinedButton("Import milestones", icon=ft.Icons.UPLOAD_FILE, on_click=import_milestones),
                    ft.Row(
                        [
                            ft.OutlinedButton("Export commitments", icon=ft.Icons.DOWNLOAD, on_click=lambda e: export_dataset("commitments", e)),
                            ft.OutlinedButton("Export decisions", icon=ft.Icons.DOWNLOAD, on_click=lambda e: export_dataset("decisions", e)),
                            ft.OutlinedButton("Export milestones", icon=ft.Icons.DOWNLOAD, on_click=lambda e: export_dataset("milestones", e)),
                        ],
                        wrap=True,
                    ),
                    import_status,
                ],
            ),
            text("Meetings", 18, ft.FontWeight.BOLD),
            *meeting_cards,
            text("Commitment dashboard", 18, ft.FontWeight.BOLD),
            ft.Row([chip("Due today"), chip("Due this week"), chip("Overdue"), chip("Awaiting evidence"), chip("Completed"), chip("Escalated")], wrap=True),
            *commitment_cards,
            text("Decision register", 18, ft.FontWeight.BOLD),
            *decision_cards,
            text("Milestone register", 18, ft.FontWeight.BOLD),
            *milestone_cards,
        ],
    )
