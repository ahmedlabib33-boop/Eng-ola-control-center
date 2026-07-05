from __future__ import annotations

import flet as ft

from ola_360.components.ui import card, chip, metric_card, text, warning_card
from ola_360.core.theme import PALETTE
from ola_360.repositories.app_repository import AppRepository
from ola_360.services.brief_service import MorningBriefService
from ola_360.services.offline_service import OfflineService
from ola_360.services.premium_service import PremiumService
from ola_360.services.report_service import ReportService
from ola_360.services.state import AppState


def home_view(repo: AppRepository, brief_service: MorningBriefService, offline_service: OfflineService, state: AppState, refresh) -> ft.Control:
    brief = brief_service.build()
    offline = offline_service.status()
    reporter = ReportService(repo, repo.db_path.parents[1] / "exports")
    premium = PremiumService(repo)
    report_status = ft.Text("", size=12, color=PALETTE.emerald, no_wrap=False)
    focus_items = premium.executive_focus()
    priority_cards = [warning_card(item) for item in brief["warnings"]]
    if not priority_cards:
        priority_cards = [card([text("No critical stored warning", 16, ft.FontWeight.BOLD), text("The brief is generated from local SQLite records.", 13, color=PALETTE.muted)])]
    focus_cards: list[ft.Control] = [
        card(
            [
                ft.Row([chip(item["kind"], PALETTE.bronze), chip(item["severity"], PALETTE.red if item["severity"] == "Critical" else PALETTE.amber)], wrap=True),
                text(item["title"], 16, ft.FontWeight.BOLD),
                text(item["detail"], 12, color=PALETTE.muted),
                text(f"Required: {item['action']}", 13),
                chip(f"Due {item['due']}", PALETTE.blue),
            ],
            accent=PALETTE.red if item["severity"] == "Critical" else PALETTE.amber,
        )
        for item in focus_items
    ]
    if not focus_cards:
        focus_cards = [
            card(
                [
                    text("No director-level intervention is currently stored.", 15, ft.FontWeight.BOLD),
                    text("Use Radar, Meetings, or imports to add live PMO data.", 13, color=PALETTE.muted),
                ],
                accent=PALETTE.emerald,
            )
        ]

    def go(tab: int, secondary: str | None = None):
        state.active_tab = tab
        state.secondary_page = secondary
        refresh()

    def generate_report(e):
        try:
            output = reporter.build_executive_report()
            report_status.value = f"Executive report generated: {output}"
            report_status.color = PALETTE.emerald
        except Exception as exc:
            report_status.value = str(exc)
            report_status.color = PALETTE.red
        e.page.update()

    return ft.ListView(
        expand=True,
        spacing=14,
        padding=ft.Padding(0, 0, 0, 20),
        controls=[
            ft.Text("Good morning, Eng. Ola", size=26, weight=ft.FontWeight.BOLD, color=PALETTE.text),
            ft.Row([text(brief["date"], 13, color=PALETTE.muted), chip(brief["time"], PALETTE.bronze)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            card(
                [
                    ft.Row([ft.Icon(ft.Icons.AUTO_AWESOME, color=PALETTE.bronze), text("Executive AI Summary", 15, ft.FontWeight.BOLD)]),
                    text(brief["summary"], 15),
                    ft.Row([chip(brief["freshness"], PALETTE.emerald), chip(f"{offline['mode']} | Sync {offline['last_sync']}", PALETTE.blue)], wrap=True),
                ],
                accent=PALETTE.bronze,
            ),
            ft.ResponsiveRow(
                [
                    ft.Container(metric_card("Critical warnings", str(brief["critical_count"]), ft.Icons.WARNING_AMBER, PALETTE.red), col={"xs": 4}),
                    ft.Container(metric_card("Decisions", str(brief["decision_count"]), ft.Icons.RULE, PALETTE.amber), col={"xs": 4}),
                    ft.Container(metric_card("Overdue", str(brief["overdue_count"]), ft.Icons.TIMER_OFF, PALETTE.plum), col={"xs": 4}),
                ],
                spacing=8,
            ),
            card(
                [
                    text("Quick actions", 16, ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            ft.IconButton(ft.Icons.ADD_ALERT, tooltip="New warning", on_click=lambda e: go(1)),
                            ft.IconButton(ft.Icons.EVENT_NOTE, tooltip="New meeting", on_click=lambda e: go(2)),
                            ft.IconButton(ft.Icons.TASK_ALT, tooltip="Commitments", on_click=lambda e: go(0, "commitments")),
                            ft.IconButton(ft.Icons.RADAR, tooltip="Intervention cockpit", on_click=lambda e: go(0, "intervention")),
                            ft.IconButton(ft.Icons.FOLDER_COPY, tooltip="Template center", on_click=lambda e: go(0, "templates")),
                            ft.IconButton(ft.Icons.NIGHTLIGHT_ROUND, tooltip="End-of-day review", on_click=lambda e: go(0, "shutdown")),
                        ],
                        wrap=True,
                    ),
                ],
                accent=PALETTE.blue,
            ),
            text("3 things requiring Eng. Ola", 18, ft.FontWeight.BOLD),
            *focus_cards,
            text("Priority cards", 18, ft.FontWeight.BOLD),
            *priority_cards,
            card(
                [
                    text("Today", 16, ft.FontWeight.BOLD),
                    text(f"Meetings: {len(brief['meetings'])}", 13),
                    text(f"Personal preview: {brief['personal_preview'][0].title if brief['personal_preview'] else 'No private reminder due'}", 13, color=PALETTE.muted),
                    ft.Row([ft.OutlinedButton("Approve"), ft.OutlinedButton("Delegate"), ft.OutlinedButton("Escalate")], wrap=True),
                ]
            ),
            ft.ExpansionTile(
                title=text("Executive reports", 16, ft.FontWeight.BOLD),
                controls=[
                    text("Generate a management-ready PMO report from stored records. Private My Day data is excluded.", 13, color=PALETTE.muted),
                    ft.ElevatedButton("Generate PMO report", icon=ft.Icons.DESCRIPTION_OUTLINED, on_click=generate_report),
                    report_status,
                ],
            ),
        ],
    )
