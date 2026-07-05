from __future__ import annotations

import flet as ft

from ola_360.core.theme import PALETTE, severity_color


def border_all(width: int, color: str) -> ft.Border:
    side = ft.BorderSide(width, color)
    return ft.Border(left=side, top=side, right=side, bottom=side)


def text(value: str, size: int = 14, weight: ft.FontWeight | None = None, color: str | None = None) -> ft.Text:
    return ft.Text(value, size=size, weight=weight, color=color or PALETTE.text, selectable=False, no_wrap=False)


def chip(label: str, color: str = PALETTE.bronze) -> ft.Container:
    return ft.Container(
        content=ft.Text(label, size=11, color=color, weight=ft.FontWeight.W_700),
        padding=ft.Padding(10, 6, 10, 6),
        border=border_all(1, color),
        border_radius=20,
    )


def card(content: list[ft.Control], accent: str | None = None, expand: bool = False) -> ft.Container:
    return ft.Container(
        content=ft.Column(content, spacing=10, tight=True),
        bgcolor=PALETTE.panel,
        border=border_all(1, accent or PALETTE.border),
        border_radius=22,
        padding=18,
        shadow=ft.BoxShadow(blur_radius=22, color="#66000000", offset=ft.Offset(0, 10)),
        expand=expand,
    )


def metric_card(title: str, value: str, icon: str, color: str) -> ft.Container:
    return card(
        [
            ft.Row([ft.Icon(icon, color=color, size=22), text(value, 28, ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            text(title, 12, color=PALETTE.muted),
        ],
        accent=color,
        expand=True,
    )


def warning_card(item, on_action=None) -> ft.Container:
    return card(
        [
            ft.Row(
                [
                    ft.Text(
                        item.title,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=PALETTE.text,
                        expand=True,
                        no_wrap=False,
                    ),
                    chip(item.severity, severity_color(item.severity)),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            text(f"{item.sector} | {item.project}", 12, color=PALETTE.muted),
            text(item.potential_impact, 13),
            ft.Row(
                [
                    chip(item.trend, PALETTE.blue),
                    chip(f"Due {item.due_date}", PALETTE.amber),
                    chip(item.owner, PALETTE.emerald),
                ],
                wrap=True,
            ),
            ft.Row(
                [
                    ft.ElevatedButton("Review", icon=ft.Icons.CHECK_CIRCLE_OUTLINE, on_click=on_action),
                    ft.OutlinedButton("Escalate", icon=ft.Icons.PRIORITY_HIGH, on_click=on_action),
                ],
                wrap=True,
            ),
        ],
        accent=severity_color(item.severity),
    )


def empty_state(title: str, body: str) -> ft.Container:
    return card(
        [
            ft.Icon(ft.Icons.INBOX_OUTLINED, color=PALETTE.muted, size=36),
            text(title, 18, ft.FontWeight.BOLD),
            text(body, 13, color=PALETTE.muted),
        ],
        accent=PALETTE.border,
    )


def loading_skeleton() -> ft.Container:
    return ft.Container(
        height=80,
        bgcolor=PALETTE.panel_2,
        border_radius=20,
        opacity=0.7,
    )
