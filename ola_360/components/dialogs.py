from __future__ import annotations

import flet as ft


def message_dialog(title: str, message: str) -> ft.AlertDialog:
    return ft.AlertDialog(title=ft.Text(title), content=ft.Text(message), actions=[ft.TextButton("Close")])
