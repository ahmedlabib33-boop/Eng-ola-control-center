from __future__ import annotations

import flet as ft

from ola_360.components.ui import card, chip, empty_state, text
from ola_360.core.theme import PALETTE
from ola_360.repositories.app_repository import AppRepository
from ola_360.services.premium_service import PremiumService
from ola_360.services.report_service import ReportService
from ola_360.services.state import AppState


def secondary_view(repo: AppRepository, state: AppState, notifications: list[str], refresh) -> ft.Control:
    page = state.secondary_page or "reports"
    title = {
        "decisions": "Decision Register",
        "commitments": "Commitment Control",
        "notifications": "Notifications",
        "reports": "Executive Reports",
        "intervention": "Intervention Cockpit",
        "timeline": "Follow-up Timeline",
        "templates": "Template Center",
        "shutdown": "End-of-Day Review",
        "settings": "Settings",
        "privacy": "Privacy Boundary",
        "help": "Help",
    }.get(page, "More")
    return ft.ListView(
        expand=True,
        spacing=12,
        padding=ft.Padding(0, 0, 0, 20),
        controls=[
            ft.Row(
                [
                    text(title, 24, ft.FontWeight.BOLD),
                    ft.OutlinedButton("Back", icon=ft.Icons.ARROW_BACK, on_click=lambda e: _close_secondary(state, refresh)),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                wrap=True,
            ),
            *_content(page, repo, state, notifications, refresh),
        ],
    )


def _close_secondary(state: AppState, refresh) -> None:
    state.secondary_page = None
    refresh()


def _content(page: str, repo: AppRepository, state: AppState, notifications: list[str], refresh) -> list[ft.Control]:
    if page == "decisions":
        return _decisions(repo, refresh)
    if page == "commitments":
        return _commitments(repo, refresh)
    if page == "notifications":
        return _notifications(notifications)
    if page == "intervention":
        return _intervention(repo, refresh)
    if page == "timeline":
        return _timeline(repo)
    if page == "templates":
        return _templates(repo)
    if page == "shutdown":
        return _shutdown(repo)
    if page == "settings":
        return _settings(state)
    if page == "privacy":
        return _privacy()
    if page == "help":
        return _help()
    return _reports(repo)


def _intervention(repo: AppRepository, refresh) -> list[ft.Control]:
    items = PremiumService(repo).intervention_items()
    if not items:
        return [empty_state("No intervention item", "Critical warnings, overdue commitments, pending decisions, and project update issues will appear here.")]
    controls: list[ft.Control] = []
    for item in items:
        accent = PALETTE.red if item["severity"] == "Critical" else PALETTE.amber
        controls.append(
            card(
                [
                    ft.Row([chip(item["kind"], PALETTE.bronze), chip(item["severity"], accent)], wrap=True),
                    text(item["title"], 17, ft.FontWeight.BOLD),
                    text(item["detail"], 12, color=PALETTE.muted),
                    text(f"Recommended intervention: {item['action']}", 13),
                    ft.Row([chip(f"Due {item['due']}", PALETTE.blue), ft.OutlinedButton("Mark reviewed", icon=ft.Icons.CHECK_CIRCLE_OUTLINE, on_click=lambda e: refresh())], wrap=True),
                ],
                accent=accent,
            )
        )
    return controls


def _timeline(repo: AppRepository) -> list[ft.Control]:
    rows = PremiumService(repo).recent_timeline()
    if not rows:
        return [empty_state("No timeline yet", "Audit events will appear after warnings, decisions, commitments, and imports are created or updated.")]
    return [
        card(
            [
                ft.Row([chip(row["entity_type"], PALETTE.blue), chip(row["action"], PALETTE.bronze)], wrap=True),
                text(f"{row['actor']} | {row['created_at']}", 12, color=PALETTE.muted),
                text(f"Record ID: {row['entity_id'] or 'n/a'}", 12),
            ],
            accent=PALETTE.border,
        )
        for row in rows
    ]


def _templates(repo: AppRepository) -> list[ft.Control]:
    rows = PremiumService(repo).template_catalog()
    if not rows:
        return [empty_state("No templates found", "Template CSV files should be stored in templates/.")]
    controls = [
        card(
            [
                text("Use these files for clean data input", 17, ft.FontWeight.BOLD),
                text("Copy the CSV headers into Excel if preferred, then import the file from the related module.", 13, color=PALETTE.muted),
            ],
            accent=PALETTE.bronze,
        )
    ]
    for row in rows:
        controls.append(
            card(
                [
                    ft.Row([text(row["name"], 15, ft.FontWeight.BOLD), chip(row["type"], PALETTE.blue)], wrap=True),
                    text(row["description"], 13),
                    text(row["path"], 11, color=PALETTE.muted),
                ],
                accent=PALETTE.border,
            )
        )
    return controls


def _shutdown(repo: AppRepository) -> list[ft.Control]:
    review = PremiumService(repo).shutdown_review()

    def lines(values: list[str], empty: str) -> ft.Control:
        return ft.Column([text(f"- {value}", 13) for value in values] or [text(empty, 13, color=PALETTE.muted)], spacing=4, tight=True)

    return [
        card(
            [
                text("Tomorrow's most important priority", 18, ft.FontWeight.BOLD),
                text(review["tomorrow_priority"], 14),
            ],
            accent=PALETTE.bronze,
        ),
        card([text("Completed today", 16, ft.FontWeight.BOLD), lines(review["completed_today"], "No completed commitment is stored today.")], accent=PALETTE.emerald),
        card([text("Still open", 16, ft.FontWeight.BOLD), lines(review["still_open"], "No open commitment is stored.")], accent=PALETTE.amber),
        card([text("Overdue", 16, ft.FontWeight.BOLD), lines(review["overdue"], "No overdue commitment is stored.")], accent=PALETTE.red),
        card([text("Pending decisions", 16, ft.FontWeight.BOLD), lines(review["pending_decisions"], "No pending or deferred decision is stored.")], accent=PALETTE.blue),
        card([text("Personal preview", 16, ft.FontWeight.BOLD), lines(review["personal_attention"], "No private task is due tomorrow.")], accent=PALETTE.plum),
    ]


def _reports(repo: AppRepository) -> list[ft.Control]:
    reporter = ReportService(repo, repo.db_path.parents[1] / "exports")
    status = ft.Text("", size=12, color=PALETTE.emerald, no_wrap=False)

    def generate(e):
        try:
            output = reporter.build_executive_report()
            status.value = f"Generated: {output}"
            status.color = PALETTE.emerald
        except Exception as exc:
            status.value = str(exc)
            status.color = PALETTE.red
        e.page.update()

    return [
        card(
            [
                text("Management-ready PMO report", 18, ft.FontWeight.BOLD),
                text("Creates a Markdown report from warnings, decisions, commitments, meetings, project updates, comments, and attachments.", 13, color=PALETTE.muted),
                text("Private My Day records are excluded.", 13, color=PALETTE.amber),
                ft.ElevatedButton("Generate report", icon=ft.Icons.DESCRIPTION_OUTLINED, on_click=generate),
                status,
            ],
            accent=PALETTE.bronze,
        )
    ]


def _decisions(repo: AppRepository, refresh) -> list[ft.Control]:
    items = repo.decisions()
    if not items:
        return [empty_state("No decisions", "Create decisions from Meetings or import the decisions template.")]
    cards: list[ft.Control] = []
    for item in items:
        cards.append(
            card(
                [
                    ft.Row([text(item.title, 16, ft.FontWeight.BOLD), chip(item.status, PALETTE.blue)], wrap=True),
                    text(f"{item.project} | Due {item.due_date}", 13, color=PALETTE.muted),
                    ft.Row(
                        [
                            ft.OutlinedButton("Approve", icon=ft.Icons.THUMB_UP_OUTLINED, on_click=lambda e, item=item: repo.update_decision_status(item.id, "Approved") or refresh()),
                            ft.OutlinedButton("Defer", icon=ft.Icons.SCHEDULE, on_click=lambda e, item=item: repo.update_decision_status(item.id, "Deferred") or refresh()),
                        ],
                        wrap=True,
                    ),
                ],
                accent=PALETTE.blue,
            )
        )
    return cards


def _commitments(repo: AppRepository, refresh) -> list[ft.Control]:
    items = repo.commitments()
    if not items:
        return [empty_state("No commitments", "Create commitments from Meetings or import the commitments template.")]
    cards: list[ft.Control] = []
    for item in items:
        color = PALETTE.red if item.status == "Overdue" else PALETTE.amber
        cards.append(
            card(
                [
                    ft.Row([text(item.title, 16, ft.FontWeight.BOLD), chip(item.status, color)], wrap=True),
                    text(f"Owner: {item.owner} | Project: {item.project} | Due {item.due_date}", 13, color=PALETTE.muted),
                    ft.Row(
                        [
                            ft.OutlinedButton("Complete", icon=ft.Icons.CHECK, on_click=lambda e, item=item: repo.update_commitment_status(item.id, "Completed", 100) or refresh()),
                            ft.OutlinedButton("Escalate", icon=ft.Icons.PRIORITY_HIGH, on_click=lambda e, item=item: repo.update_commitment_status(item.id, "Escalated") or refresh()),
                        ],
                        wrap=True,
                    ),
                ],
                accent=color,
            )
        )
    return cards


def _notifications(notifications: list[str]) -> list[ft.Control]:
    if not notifications:
        return [empty_state("No notifications", "Critical warnings, due decisions, and stale updates will appear here.")]
    return [card([text(item, 14)], accent=PALETTE.amber) for item in notifications]


def _settings(state: AppState) -> list[ft.Control]:
    return [
        card([text("Mode", 16, ft.FontWeight.BOLD), ft.Row([chip(state.theme_mode.title(), PALETTE.plum), chip(state.language.upper(), PALETTE.blue)], wrap=True)]),
        card([text("Authentication", 16, ft.FontWeight.BOLD), text("Login is disabled for the current local build. The app opens directly as Eng. Ola.", 13, color=PALETTE.muted)]),
        card([text("Storage", 16, ft.FontWeight.BOLD), text("Local SQLite data is stored in the app data folder and templates live in templates/.", 13, color=PALETTE.muted)]),
    ]


def _privacy() -> list[ft.Control]:
    return [
        card(
            [
                text("Private data isolation", 18, ft.FontWeight.BOLD),
                text("My Day uses separate private tables and does not feed PMO reports, organizational AI answers, or corporate exports.", 13),
                ft.Row([chip("Separate tables", PALETTE.emerald), chip("No PMO reports", PALETTE.amber), chip("Private module only", PALETTE.blue)], wrap=True),
            ],
            accent=PALETTE.emerald,
        )
    ]


def _help() -> list[ft.Control]:
    return [
        card([text("Run", 16, ft.FontWeight.BOLD), text("Use RUN_APP.bat from D:\\Eng. OLA. The web app opens on http://127.0.0.1:6194.", 13, color=PALETTE.muted)]),
        card([text("Data input", 16, ft.FontWeight.BOLD), text("Use templates/ CSV files for imports. Paste meeting notes into Meetings to extract actions, decisions, minutes, and follow-up drafts.", 13, color=PALETTE.muted)]),
        card([text("Reports", 16, ft.FontWeight.BOLD), text("Generate PMO reports from Home or More > Reports. Outputs are written to exports/.", 13, color=PALETTE.muted)]),
    ]
