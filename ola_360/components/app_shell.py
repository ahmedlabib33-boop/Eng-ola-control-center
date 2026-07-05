from __future__ import annotations

import flet as ft

from ola_360.components.bottom_navigation import bottom_navigation
from ola_360.core.config import Settings
from ola_360.core.localization import is_rtl, tr
from ola_360.core.theme import PALETTE
from ola_360.services.state import AppState


def shell(
    settings: Settings,
    state: AppState,
    content: ft.Control,
    on_nav,
    on_language_toggle=None,
    on_theme_toggle=None,
    on_notifications_toggle=None,
    on_more=None,
) -> ft.View:
    notification_panel = ft.Container()
    if state.notifications_open:
        notification_panel = ft.Container(
            padding=ft.Padding(18, 0, 18, 8),
            content=ft.Container(
                padding=12,
                border_radius=14,
                bgcolor=PALETTE.panel_2,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(tr("notifications", state.language), size=15, weight=ft.FontWeight.BOLD, color=PALETTE.text),
                                ft.TextButton("Close", on_click=on_notifications_toggle),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        *[ft.Text(item, size=12, color=PALETTE.muted) for item in (state.notifications or ["No current notifications."])[:5]],
                    ],
                    tight=True,
                    spacing=6,
                ),
            ),
        )
    return ft.View(
        route="/app",
        bgcolor=PALETTE.bg,
        padding=0,
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(settings.app_name, size=23, weight=ft.FontWeight.BOLD, color=PALETTE.text),
                                            ft.Text(
                                                f"{settings.subtitle} | {'AR' if state.language == 'ar' else 'EN'} | {state.theme_mode.title()}",
                                                size=12,
                                                color=PALETTE.bronze,
                                            ),
                                        ],
                                        spacing=0,
                                    ),
                                    ft.Row(
                                        [
                                            ft.IconButton(ft.Icons.LANGUAGE, tooltip=tr("language", state.language), on_click=on_language_toggle),
                                            ft.IconButton(ft.Icons.DARK_MODE, tooltip=tr("theme", state.language), on_click=on_theme_toggle),
                                            ft.IconButton(
                                                ft.Icons.NOTIFICATIONS,
                                                tooltip=f"{tr('notifications', state.language)} ({len(state.notifications)})",
                                                on_click=on_notifications_toggle,
                                            ),
                                            ft.PopupMenuButton(
                                                icon=ft.Icons.MORE_VERT,
                                                tooltip="More",
                                                on_select=on_more,
                                                items=[
                                                    ft.PopupMenuItem(content="Reports", data="reports"),
                                                    ft.PopupMenuItem(content="Intervention Cockpit", data="intervention"),
                                                    ft.PopupMenuItem(content="Decisions", data="decisions"),
                                                    ft.PopupMenuItem(content="Commitments", data="commitments"),
                                                    ft.PopupMenuItem(content="Follow-up Timeline", data="timeline"),
                                                    ft.PopupMenuItem(content="Template Center", data="templates"),
                                                    ft.PopupMenuItem(content="End-of-Day Review", data="shutdown"),
                                                    ft.PopupMenuItem(content="Notifications", data="notifications"),
                                                    ft.PopupMenuItem(content="Settings", data="settings"),
                                                    ft.PopupMenuItem(content="Privacy", data="privacy"),
                                                    ft.PopupMenuItem(content="Help", data="help"),
                                                ],
                                            ),
                                        ]
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            padding=ft.Padding(18, 12, 18, 8),
                        ),
                        notification_panel,
                        ft.Container(content=content, expand=True, padding=ft.Padding(14, 0, 14, 0)),
                        bottom_navigation(state.active_tab, on_nav, state.language),
                    ],
                    expand=True,
                    spacing=0,
                    rtl=is_rtl(state.language),
                ),
            )
        ],
    )
