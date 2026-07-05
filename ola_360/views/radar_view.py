from __future__ import annotations

from datetime import date, timedelta

import flet as ft

from ola_360.components.forms import dropdown, input_field
from ola_360.components.ui import chip, text, warning_card
from ola_360.core.theme import PALETTE
from ola_360.repositories.app_repository import AppRepository
from ola_360.services.export_service import ExportService
from ola_360.services.import_service import ImportService
from ola_360.services.state import AppState


def radar_view(repo: AppRepository, state: AppState, refresh) -> ft.Control:
    importer = ImportService(repo)
    exporter = ExportService(repo, repo.db_path.parents[1] / "exports")
    sector = dropdown("Sector", ["All", "Buildings", "Tunnels", "Infrastructure", "Roads", "Other"], state.selected_sector)
    severity = dropdown("Severity", ["All", "Information", "Watch", "Intervention", "Critical"], state.warning_severity)
    entry_category = dropdown("Category", ["Schedule", "Progress", "Engineering", "Procurement", "Commercial", "Risk", "Governance", "Data quality", "Meeting commitment", "Management decision"])
    entry_sector = dropdown("Entry sector", ["Buildings", "Tunnels", "Infrastructure", "Roads", "Other"])
    entry_severity = dropdown("Entry severity", ["Information", "Watch", "Intervention", "Critical"], "Watch")
    entry_trend = dropdown("Trend", ["New", "Stable", "Improving", "Deteriorating", "Repeated", "Closed"], "New")
    title = input_field("Warning title")
    project = input_field("Project")
    owner = input_field("Owner")
    due_date = input_field("Due date YYYY-MM-DD")
    evidence = ft.TextField(label="Evidence", multiline=True, min_lines=2, border_radius=14)
    potential_impact = ft.TextField(label="Potential effect / business impact", multiline=True, min_lines=2, border_radius=14)
    impacted_milestone = input_field("Impacted milestone")
    recommended_intervention = ft.TextField(label="Recommended intervention", multiline=True, min_lines=2, border_radius=14)
    source = input_field("Source")
    import_path = input_field("Warnings CSV/XLSX path")
    update_project = input_field("Update project")
    update_sector = dropdown("Update sector", ["Buildings", "Tunnels", "Infrastructure", "Roads", "Other"])
    update_date = input_field("Update date YYYY-MM-DD")
    update_progress = input_field("Progress %")
    update_summary = ft.TextField(label="Project update summary", multiline=True, min_lines=2, border_radius=14)
    update_next_milestone = input_field("Next milestone")
    update_issues = ft.TextField(label="Open issues", multiline=True, min_lines=2, border_radius=14)
    update_import_path = input_field("Project updates CSV/XLSX path")
    master_project_name = input_field("Project name")
    master_project_sector = dropdown("Project sector", ["Buildings", "Tunnels", "Infrastructure", "Roads", "Other"])
    master_project_status = dropdown("Project status", ["Active", "On Hold", "Closed"], "Active")
    master_import_path = input_field("Projects CSV/XLSX path")
    comment_entity_type = dropdown("Comment entity", ["warning", "meeting", "commitment", "decision", "project", "project_update"], "warning")
    comment_entity_id = input_field("Comment entity ID")
    comment_body = ft.TextField(label="Management comment / evidence note", multiline=True, min_lines=2, border_radius=14)
    attachment_entity_type = dropdown("Attachment entity", ["warning", "meeting", "commitment", "decision", "project", "project_update"], "meeting")
    attachment_entity_id = input_field("Attachment entity ID")
    attachment_name = input_field("Attachment file name")
    attachment_path = input_field("Attachment path or reference")
    evidence_import_path = input_field("Comments or attachments CSV/XLSX path")
    entry_status = ft.Text("", color=PALETTE.emerald)
    import_status = ft.Text("", color=PALETTE.emerald)
    update_status = ft.Text("", color=PALETTE.emerald)
    master_status = ft.Text("", color=PALETTE.emerald)

    def apply_filters(e):
        state.selected_sector = sector.value
        state.warning_severity = severity.value
        refresh()

    def create(e):
        try:
            repo.create_warning(
                {
                    "title": title.value,
                    "category": entry_category.value,
                    "sector": entry_sector.value,
                    "project": project.value or "Configured PMO Project",
                    "severity": entry_severity.value,
                    "trend": entry_trend.value,
                    "owner": owner.value or "Unassigned",
                    "due_date": due_date.value or (date.today() + timedelta(days=2)).isoformat(),
                    "evidence": evidence.value or "Manual warning entered by Eng. Ola.",
                    "potential_impact": potential_impact.value or "Requires PMO review before executive reporting.",
                    "impacted_milestone": impacted_milestone.value,
                    "recommended_intervention": recommended_intervention.value or "Assign owner and request clarification.",
                    "source": source.value or "Manual PMO entry",
                }
            )
            entry_status.value = "Warning created from reviewed manual entry."
            for control in [title, project, owner, due_date, evidence, potential_impact, impacted_milestone, recommended_intervention, source]:
                control.value = ""
            refresh()
        except Exception as exc:
            entry_status.value = str(exc)
            entry_status.color = PALETTE.red
            e.page.update()

    def import_warnings(e):
        try:
            result = importer.import_file(import_path.value, "warnings")
            import_status.value = f"Imported {result['imported']} warning row(s)."
            import_status.color = PALETTE.emerald if not result["errors"] else PALETTE.amber
            if result["errors"]:
                import_status.value += " Review: " + "; ".join(result["errors"][:3])
            refresh()
        except Exception as exc:
            import_status.value = str(exc)
            import_status.color = PALETTE.red
            e.page.update()

    def export_warnings(e):
        try:
            output = exporter.export("warnings")
            import_status.value = f"Warnings exported: {output}"
            import_status.color = PALETTE.emerald
            e.page.update()
        except Exception as exc:
            import_status.value = str(exc)
            import_status.color = PALETTE.red
            e.page.update()

    def create_project_update(e):
        try:
            repo.create_project_update(
                {
                    "project": update_project.value or "Configured PMO Project",
                    "sector": update_sector.value,
                    "update_date": update_date.value or date.today().isoformat(),
                    "progress": update_progress.value or "0",
                    "summary": update_summary.value or "Manual progress update entered for PMO review.",
                    "next_milestone": update_next_milestone.value,
                    "issues": update_issues.value,
                    "source": "Manual PMO entry",
                }
            )
            update_status.value = "Project update saved and available for Morning Brief freshness checks."
            for control in [update_project, update_date, update_progress, update_summary, update_next_milestone, update_issues]:
                control.value = ""
            refresh()
        except Exception as exc:
            update_status.value = str(exc)
            update_status.color = PALETTE.red
            e.page.update()

    def import_project_updates(e):
        try:
            result = importer.import_file(update_import_path.value, "project_updates")
            update_status.value = f"Imported {result['imported']} project update row(s)."
            update_status.color = PALETTE.emerald if not result["errors"] else PALETTE.amber
            if result["errors"]:
                update_status.value += " Review: " + "; ".join(result["errors"][:3])
            refresh()
        except Exception as exc:
            update_status.value = str(exc)
            update_status.color = PALETTE.red
            e.page.update()

    def export_project_updates(e):
        try:
            output = exporter.export("project_updates")
            update_status.value = f"Project updates exported: {output}"
            update_status.color = PALETTE.emerald
            e.page.update()
        except Exception as exc:
            update_status.value = str(exc)
            update_status.color = PALETTE.red
            e.page.update()

    def create_project_master(e):
        try:
            repo.create_project_from_data(
                {
                    "name": master_project_name.value,
                    "sector": master_project_sector.value,
                    "status": master_project_status.value,
                }
            )
            master_status.value = "Project master record saved."
            master_project_name.value = ""
            refresh()
        except Exception as exc:
            master_status.value = str(exc)
            master_status.color = PALETTE.red
            e.page.update()

    def create_comment(e):
        try:
            repo.create_comment_from_data(
                {
                    "entity_type": comment_entity_type.value,
                    "entity_id": comment_entity_id.value or "1",
                    "author": "Eng. Ola",
                    "body": comment_body.value,
                }
            )
            master_status.value = "Comment saved to evidence library."
            comment_body.value = ""
            refresh()
        except Exception as exc:
            master_status.value = str(exc)
            master_status.color = PALETTE.red
            e.page.update()

    def create_attachment(e):
        try:
            repo.create_attachment_from_data(
                {
                    "entity_type": attachment_entity_type.value,
                    "entity_id": attachment_entity_id.value or "1",
                    "file_name": attachment_name.value,
                    "file_path": attachment_path.value,
                }
            )
            master_status.value = "Attachment reference saved."
            attachment_name.value = ""
            attachment_path.value = ""
            refresh()
        except Exception as exc:
            master_status.value = str(exc)
            master_status.color = PALETTE.red
            e.page.update()

    def import_master_dataset(path_field, dataset: str, label: str, e):
        try:
            result = importer.import_file(path_field.value, dataset)
            master_status.value = f"Imported {result['imported']} {label} row(s)."
            master_status.color = PALETTE.emerald if not result["errors"] else PALETTE.amber
            if result["errors"]:
                master_status.value += " Review: " + "; ".join(result["errors"][:3])
            refresh()
        except Exception as exc:
            master_status.value = str(exc)
            master_status.color = PALETTE.red
            e.page.update()

    def export_master_dataset(dataset: str, label: str, e):
        try:
            output = exporter.export(dataset)
            master_status.value = f"{label} exported: {output}"
            master_status.color = PALETTE.emerald
            e.page.update()
        except Exception as exc:
            master_status.value = str(exc)
            master_status.color = PALETTE.red
            e.page.update()

    def warning_item_card(item):
        edit_title = input_field("Edit title", item.title)
        edit_owner = input_field("Edit owner", item.owner)
        edit_due = input_field("Edit due date", item.due_date)
        edit_status = ft.Text("", color=PALETTE.emerald, size=12, no_wrap=False)

        def save_edit(e):
            try:
                repo.update_warning_core(item.id, edit_title.value, edit_owner.value, edit_due.value)
                refresh()
            except Exception as exc:
                edit_status.value = str(exc)
                edit_status.color = PALETTE.red
                e.page.update()

        return ft.Column(
            [
                warning_card(item, on_action=lambda e, item=item: repo.update_warning_status(item.id, "Reviewed") or refresh()),
                ft.ExpansionTile(
                    title=text("Details and correction", 13, ft.FontWeight.BOLD),
                    controls=[
                        text(f"Evidence: {item.evidence}", 12, color=PALETTE.muted),
                        text(f"Impact: {item.potential_impact}", 12, color=PALETTE.muted),
                        text(f"Intervention: {item.recommended_intervention}", 12, color=PALETTE.muted),
                        edit_title,
                        edit_owner,
                        edit_due,
                        ft.Row(
                            [
                                ft.OutlinedButton("Save correction", icon=ft.Icons.SAVE, on_click=save_edit),
                                ft.OutlinedButton("Close", icon=ft.Icons.CHECK, on_click=lambda e, item=item: repo.update_warning_status(item.id, "Closed") or refresh()),
                                ft.OutlinedButton("Delete", icon=ft.Icons.DELETE_OUTLINE, on_click=lambda e, item=item: repo.delete_record("warning", item.id) or refresh()),
                            ],
                            wrap=True,
                        ),
                        edit_status,
                    ],
                ),
            ],
            spacing=4,
        )

    warnings = repo.warnings(state.selected_sector, state.warning_severity)
    return ft.ListView(
        expand=True,
        spacing=12,
        controls=[
            text("Early-Warning Radar", 24, ft.FontWeight.BOLD),
            ft.Row([sector, severity, ft.IconButton(ft.Icons.FILTER_ALT, on_click=apply_filters)], vertical_alignment=ft.CrossAxisAlignment.END),
            ft.ExpansionTile(
                title=text("Create reviewed warning", 16, ft.FontWeight.BOLD),
                controls=[
                    title,
                    ft.Row([entry_category, entry_sector], wrap=True),
                    ft.Row([entry_severity, entry_trend], wrap=True),
                    project,
                    owner,
                    due_date,
                    evidence,
                    potential_impact,
                    impacted_milestone,
                    recommended_intervention,
                    source,
                    ft.ElevatedButton("Save warning", icon=ft.Icons.SAVE, on_click=create),
                    entry_status,
                ],
            ),
            ft.ExpansionTile(
                title=text("Import warning template", 16, ft.FontWeight.BOLD),
                controls=[
                    text("Use templates/warnings_template.csv or templates/critical_issues_template.csv. CSV and XLSX are supported.", 12, color=PALETTE.muted),
                    import_path,
                    ft.ElevatedButton("Import warnings", icon=ft.Icons.UPLOAD_FILE, on_click=import_warnings),
                    ft.OutlinedButton("Export warnings", icon=ft.Icons.DOWNLOAD, on_click=export_warnings),
                    import_status,
                ],
            ),
            ft.ExpansionTile(
                title=text("Project updates and data freshness", 16, ft.FontWeight.BOLD),
                controls=[
                    text("Add or import PMO project updates. Old or missing updates trigger management notifications.", 12, color=PALETTE.muted),
                    update_project,
                    update_sector,
                    update_date,
                    update_progress,
                    update_summary,
                    update_next_milestone,
                    update_issues,
                    ft.ElevatedButton("Save project update", icon=ft.Icons.SAVE, on_click=create_project_update),
                    update_import_path,
                    ft.OutlinedButton("Import project updates", icon=ft.Icons.UPLOAD_FILE, on_click=import_project_updates),
                    ft.OutlinedButton("Export project updates", icon=ft.Icons.DOWNLOAD, on_click=export_project_updates),
                    update_status,
                    *[
                        ft.Container(
                            padding=10,
                            border_radius=12,
                            bgcolor=PALETTE.panel_2,
                            content=ft.Column(
                                [
                                    text(f"{item.project} | {item.update_date} | {item.progress}%", 14, ft.FontWeight.BOLD),
                                    text(item.summary, 12, color=PALETTE.muted),
                                    text(f"Issues: {item.issues or 'None recorded'}", 12, color=PALETTE.muted),
                                ],
                                tight=True,
                                spacing=4,
                            ),
                        )
                        for item in repo.project_updates()[:4]
                    ],
                ],
            ),
            ft.ExpansionTile(
                title=text("Project master and evidence library", 16, ft.FontWeight.BOLD),
                controls=[
                    text("Maintain project master data and link comments or attachment references to any PMO entity.", 12, color=PALETTE.muted),
                    master_project_name,
                    master_project_sector,
                    master_project_status,
                    ft.ElevatedButton("Save project", icon=ft.Icons.DOMAIN_ADD, on_click=create_project_master),
                    master_import_path,
                    ft.OutlinedButton("Import projects", icon=ft.Icons.UPLOAD_FILE, on_click=lambda e: import_master_dataset(master_import_path, "projects", "project", e)),
                    ft.OutlinedButton("Export projects", icon=ft.Icons.DOWNLOAD, on_click=lambda e: export_master_dataset("projects", "Projects", e)),
                    comment_entity_type,
                    comment_entity_id,
                    comment_body,
                    ft.OutlinedButton("Save comment", icon=ft.Icons.COMMENT, on_click=create_comment),
                    attachment_entity_type,
                    attachment_entity_id,
                    attachment_name,
                    attachment_path,
                    ft.OutlinedButton("Save attachment reference", icon=ft.Icons.ATTACH_FILE, on_click=create_attachment),
                    evidence_import_path,
                    ft.Row(
                        [
                            ft.OutlinedButton("Import comments", icon=ft.Icons.UPLOAD_FILE, on_click=lambda e: import_master_dataset(evidence_import_path, "comments", "comment", e)),
                            ft.OutlinedButton("Import attachments", icon=ft.Icons.UPLOAD_FILE, on_click=lambda e: import_master_dataset(evidence_import_path, "attachments", "attachment", e)),
                        ],
                        wrap=True,
                    ),
                    ft.Row(
                        [
                            ft.OutlinedButton("Export comments", icon=ft.Icons.DOWNLOAD, on_click=lambda e: export_master_dataset("comments", "Comments", e)),
                            ft.OutlinedButton("Export attachments", icon=ft.Icons.DOWNLOAD, on_click=lambda e: export_master_dataset("attachments", "Attachments", e)),
                        ],
                        wrap=True,
                    ),
                    master_status,
                    text("Recent projects", 14, ft.FontWeight.BOLD),
                    *[text(f"{item.id} | {item.name} | {item.sector} | {item.status}", 12, color=PALETTE.muted) for item in repo.projects()[:5]],
                    text("Recent comments and attachments", 14, ft.FontWeight.BOLD),
                    *[text(f"Comment #{item.id} -> {item.entity_type}:{item.entity_id} | {item.body[:80]}", 12, color=PALETTE.muted) for item in repo.comments()[:3]],
                    *[text(f"Attachment #{item.id} -> {item.entity_type}:{item.entity_id} | {item.file_name}", 12, color=PALETTE.muted) for item in repo.attachments()[:3]],
                ],
            ),
            ft.Row([chip("Review"), chip("Assign"), chip("Delegate"), chip("Escalate"), chip("Close with evidence")], wrap=True),
            *[warning_item_card(item) for item in warnings],
        ],
    )
