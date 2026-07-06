from __future__ import annotations

from datetime import date

import flet as ft

from ola_360.components.forms import dropdown, input_field
from ola_360.components.ui import card, chip, text
from ola_360.core.theme import PALETTE
from ola_360.repositories.app_repository import AppRepository
from ola_360.services.auth_service import AuthService
from ola_360.services.export_service import ExportService
from ola_360.services.import_service import ImportService
from ola_360.services.speech_service import SpeechToTextService
from ola_360.services.state import AppState


def my_day_view(repo: AppRepository, auth: AuthService, state: AppState, refresh) -> ft.Control:
    if not auth.can_access_private(state.user):
        return card(
            [
                ft.Icon(ft.Icons.LOCK, color=PALETTE.red),
                text("Private area locked", 20, ft.FontWeight.BOLD),
                text("Only Eng. Ola can access this isolated module.", 13, color=PALETTE.muted),
            ]
        )

    importer = ImportService(repo)
    exporter = ExportService(repo, repo.db_path.parents[1] / "exports")
    speech = SpeechToTextService()
    title = input_field("Private task")
    category = dropdown("Category", ["Priority", "Family", "Call", "Errand", "Wellbeing", "Note"])
    due_date = input_field("Due date YYYY-MM-DD")
    import_path = input_field("Private tasks CSV/XLSX path")
    event_title = input_field("Personal appointment / reminder")
    event_category = dropdown("Event category", ["Family", "Doctor", "Car", "Travel", "Document renewal", "Gift", "Important call", "Personal"])
    event_date = input_field("Event date YYYY-MM-DD")
    event_import_path = input_field("Personal events CSV/XLSX path")
    note_title = input_field("Private note title")
    note_body = ft.TextField(label="Private note / idea", multiline=True, min_lines=3, border_radius=14)
    voice_path = input_field("Voice thought audio file path")
    note_import_path = input_field("Private notes CSV/XLSX path")
    wellbeing_date = input_field("Check-in date YYYY-MM-DD")
    water_done = ft.Checkbox(label="Water reminder completed")
    break_done = ft.Checkbox(label="Break reminder completed")
    stress_level = dropdown("Stress level", ["1", "2", "3", "4", "5"])
    wellbeing_import_path = input_field("Wellbeing check-ins CSV/XLSX path")
    status = ft.Text("", color=PALETTE.emerald, size=12, no_wrap=False)

    def add_task(e):
        repo.create_private_task(title.value, category.value, due_date.value or date.today().isoformat())
        title.value = ""
        due_date.value = ""
        refresh()

    def import_private_tasks(e):
        try:
            result = importer.import_file(import_path.value, "personal_tasks")
            status.value = f"Imported {result['imported']} private task row(s)."
            status.color = PALETTE.emerald if not result["errors"] else PALETTE.amber
            if result["errors"]:
                status.value += " Review: " + "; ".join(result["errors"][:3])
            refresh()
        except Exception as exc:
            status.value = str(exc)
            status.color = PALETTE.red
            e.page.update()

    def add_event(e):
        try:
            repo.create_personal_event(event_title.value, event_date.value or date.today().isoformat(), event_category.value)
            event_title.value = ""
            event_date.value = ""
            refresh()
        except Exception as exc:
            status.value = str(exc)
            status.color = PALETTE.red
            e.page.update()

    def add_note(e):
        try:
            repo.create_private_note(note_title.value, note_body.value or "")
            note_title.value = ""
            note_body.value = ""
            refresh()
        except Exception as exc:
            status.value = str(exc)
            status.color = PALETTE.red
            e.page.update()

    def transcribe_voice_note(e):
        try:
            result = speech.transcribe_file(voice_path.value.strip())
            repo.create_voice_capture("private_note", result["source_path"], result["transcript"], "My Day - Private")
            repo.create_private_note(note_title.value or "Voice quick capture", result["transcript"])
            voice_path.value = ""
            note_title.value = ""
            status.value = "Voice quick capture transcribed and saved as a private note."
            status.color = PALETTE.emerald
            refresh()
        except Exception as exc:
            status.value = str(exc)
            status.color = PALETTE.red
            e.page.update()

    def add_wellbeing(e):
        try:
            repo.create_wellbeing_checkin(wellbeing_date.value or date.today().isoformat(), int(bool(water_done.value)), int(bool(break_done.value)), int(stress_level.value or 3))
            wellbeing_date.value = ""
            water_done.value = False
            break_done.value = False
            refresh()
        except Exception as exc:
            status.value = str(exc)
            status.color = PALETTE.red
            e.page.update()

    def import_dataset(path_field, dataset: str, label: str, e):
        try:
            result = importer.import_file(path_field.value, dataset)
            status.value = f"Imported {result['imported']} {label} row(s)."
            status.color = PALETTE.emerald if not result["errors"] else PALETTE.amber
            if result["errors"]:
                status.value += " Review: " + "; ".join(result["errors"][:3])
            refresh()
        except Exception as exc:
            status.value = str(exc)
            status.color = PALETTE.red
            e.page.update()

    def export_private_tasks(e):
        try:
            output = exporter.export("private_tasks")
            status.value = f"Private tasks exported from private module: {output}"
            status.color = PALETTE.emerald
            e.page.update()
        except Exception as exc:
            status.value = str(exc)
            status.color = PALETTE.red
            e.page.update()

    def export_dataset(dataset: str, label: str, e):
        try:
            output = exporter.export(dataset)
            status.value = f"{label} exported from private module: {output}"
            status.color = PALETTE.emerald
            e.page.update()
        except Exception as exc:
            status.value = str(exc)
            status.color = PALETTE.red
            e.page.update()

    tasks = repo.private_tasks()
    events = repo.personal_events()
    notes = repo.private_notes()
    checkins = repo.wellbeing_checkins()
    def private_task_card(item):
        edit_title = input_field("Edit private task", item.title)
        edit_category = input_field("Edit category", item.category)
        edit_due = input_field("Edit due date", item.due_date)
        edit_status = ft.Text("", color=PALETTE.emerald, size=12, no_wrap=False)

        def save_edit(e):
            try:
                repo.update_private_task_core(item.id, edit_title.value, edit_category.value, edit_due.value)
                refresh()
            except Exception as exc:
                edit_status.value = str(exc)
                edit_status.color = PALETTE.red
                e.page.update()

        return card(
            [
                ft.Row([text(item.title, 15, ft.FontWeight.BOLD), chip(item.status, PALETTE.bronze)], wrap=True),
                text(f"{item.category} | {item.due_date}", 12, color=PALETTE.muted),
                ft.Row(
                    [
                        ft.OutlinedButton("Close", icon=ft.Icons.CHECK, on_click=lambda e, item=item: repo.update_private_task_status(item.id, "Closed") or refresh()),
                        ft.OutlinedButton("Move tomorrow", icon=ft.Icons.TODAY, on_click=lambda e, item=item: repo.update_private_task_status(item.id, "Move to tomorrow") or refresh()),
                        ft.OutlinedButton("Cancel", icon=ft.Icons.CLOSE, on_click=lambda e, item=item: repo.update_private_task_status(item.id, "Canceled") or refresh()),
                        ft.OutlinedButton("Delete", icon=ft.Icons.DELETE_OUTLINE, on_click=lambda e, item=item: repo.delete_record("private_task", item.id) or refresh()),
                    ],
                    wrap=True,
                ),
                ft.ExpansionTile(
                    title=text("Edit private item", 13, ft.FontWeight.BOLD),
                    controls=[edit_title, edit_category, edit_due, ft.OutlinedButton("Save correction", icon=ft.Icons.SAVE, on_click=save_edit), edit_status],
                ),
            ]
        )

    task_cards = [private_task_card(item) for item in tasks]
    event_cards = [
        card(
            [
                ft.Row([text(item.title, 15, ft.FontWeight.BOLD), chip(item.category, PALETTE.blue)], wrap=True),
                text(item.event_date, 12, color=PALETTE.muted),
                ft.OutlinedButton("Delete", icon=ft.Icons.DELETE_OUTLINE, on_click=lambda e, item=item: repo.delete_record("personal_event", item.id) or refresh()),
            ]
        )
        for item in events[:8]
    ]
    note_cards = [
        card(
            [
                text(item.title, 15, ft.FontWeight.BOLD),
                text(item.body[:220] or "No note body.", 13, color=PALETTE.muted),
                ft.OutlinedButton("Delete", icon=ft.Icons.DELETE_OUTLINE, on_click=lambda e, item=item: repo.delete_record("private_note", item.id) or refresh()),
            ]
        )
        for item in notes[:6]
    ]
    wellbeing_cards = [
        card(
            [
                ft.Row([text(item.checkin_date, 15, ft.FontWeight.BOLD), chip(f"Stress {item.stress_level}/5", PALETTE.bronze)], wrap=True),
                ft.Row([chip("Water done" if item.water else "Water open"), chip("Break done" if item.break_done else "Break open")], wrap=True),
                ft.OutlinedButton("Delete", icon=ft.Icons.DELETE_OUTLINE, on_click=lambda e, item=item: repo.delete_record("wellbeing_checkin", item.id) or refresh()),
            ]
        )
        for item in checkins[:5]
    ]

    return ft.ListView(
        expand=True,
        spacing=12,
        controls=[
            ft.Row([text("My Day - Private", 24, ft.FontWeight.BOLD), chip("Private boundary", PALETTE.emerald)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            text("Private records never appear in PMO reports, organizational AI answers, exports, or analytics.", 13, color=PALETTE.muted),
            card([text("Top three priorities", 17, ft.FontWeight.BOLD), *[text(item.title, 14) for item in tasks[:3]]], accent=PALETTE.emerald),
            card([text("Today and upcoming personal reminders", 17, ft.FontWeight.BOLD), *[text(f"{item.event_date} | {item.title}", 14) for item in events[:3]]], accent=PALETTE.blue),
            ft.ExpansionTile(title=text("Add private item", 16, ft.FontWeight.BOLD), controls=[title, category, due_date, ft.ElevatedButton("Save private item", icon=ft.Icons.SAVE, on_click=add_task)]),
            ft.ExpansionTile(title=text("Appointments and family reminders", 16, ft.FontWeight.BOLD), controls=[event_title, event_category, event_date, ft.ElevatedButton("Save personal reminder", icon=ft.Icons.EVENT, on_click=add_event), *event_cards]),
            ft.ExpansionTile(
                title=text("Private notes and ideas", 16, ft.FontWeight.BOLD),
                controls=[
                    note_title,
                    note_body,
                    ft.ElevatedButton("Save private note", icon=ft.Icons.NOTE_ADD, on_click=add_note),
                    text(speech.status(), 12, color=PALETTE.muted),
                    voice_path,
                    ft.OutlinedButton("Transcribe voice thought", icon=ft.Icons.RECORD_VOICE_OVER, on_click=transcribe_voice_note),
                    *note_cards,
                ],
            ),
            ft.ExpansionTile(
                title=text("Wellbeing check-in", 16, ft.FontWeight.BOLD),
                controls=[
                    text("Non-medical reminders only: water, break, focus, and stress check-in.", 12, color=PALETTE.muted),
                    wellbeing_date,
                    water_done,
                    break_done,
                    stress_level,
                    ft.ElevatedButton("Save wellbeing check-in", icon=ft.Icons.SELF_IMPROVEMENT, on_click=add_wellbeing),
                    *wellbeing_cards,
                ],
            ),
            ft.ExpansionTile(
                title=text("Import and export private templates", 16, ft.FontWeight.BOLD),
                controls=[
                    text("Use the private templates folder headers as CSV or XLSX. These records remain inside the private boundary.", 12, color=PALETTE.muted),
                    import_path,
                    ft.OutlinedButton("Import private tasks", icon=ft.Icons.UPLOAD_FILE, on_click=import_private_tasks),
                    ft.OutlinedButton("Export private tasks", icon=ft.Icons.DOWNLOAD, on_click=export_private_tasks),
                    event_import_path,
                    ft.OutlinedButton("Import personal events", icon=ft.Icons.UPLOAD_FILE, on_click=lambda e: import_dataset(event_import_path, "personal_events", "personal event", e)),
                    ft.OutlinedButton("Export personal events", icon=ft.Icons.DOWNLOAD, on_click=lambda e: export_dataset("personal_events", "Personal events", e)),
                    note_import_path,
                    ft.OutlinedButton("Import private notes", icon=ft.Icons.UPLOAD_FILE, on_click=lambda e: import_dataset(note_import_path, "private_notes", "private note", e)),
                    ft.OutlinedButton("Export private notes", icon=ft.Icons.DOWNLOAD, on_click=lambda e: export_dataset("private_notes", "Private notes", e)),
                    wellbeing_import_path,
                    ft.OutlinedButton("Import wellbeing check-ins", icon=ft.Icons.UPLOAD_FILE, on_click=lambda e: import_dataset(wellbeing_import_path, "wellbeing_checkins", "wellbeing check-in", e)),
                    ft.OutlinedButton("Export wellbeing check-ins", icon=ft.Icons.DOWNLOAD, on_click=lambda e: export_dataset("wellbeing_checkins", "Wellbeing check-ins", e)),
                    status,
                ],
            ),
            card([text("End-of-day review", 17, ft.FontWeight.BOLD), ft.Row([chip("Completed"), chip("Open"), chip("Delegate"), chip("Tomorrow priority")], wrap=True)]),
            *task_cards,
        ],
    )
