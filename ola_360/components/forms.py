from __future__ import annotations

import flet as ft


def input_field(label: str, value: str = "", password: bool = False) -> ft.TextField:
    return ft.TextField(label=label, value=value, password=password, can_reveal_password=password, border_radius=14)


def dropdown(label: str, options: list[str], value: str | None = None) -> ft.Dropdown:
    return ft.Dropdown(label=label, value=value or options[0], options=[ft.dropdown.Option(item) for item in options], border_radius=14)
