from __future__ import annotations

import flet as ft

from ola_360.components.ui import card, chip, text
from ola_360.core.theme import PALETTE
from ola_360.services.state import AppState


def settings_view(state: AppState) -> ft.Control:
    return ft.ListView(
        expand=True,
        spacing=12,
        controls=[
            text("Settings and Privacy", 24, ft.FontWeight.BOLD),
            card([text("Language", 16, ft.FontWeight.BOLD), ft.Row([chip("English", PALETTE.blue), chip("Arabic RTL ready", PALETTE.bronze)])]),
            card([text("Theme", 16, ft.FontWeight.BOLD), ft.Row([chip("Dark Intelligence", PALETTE.plum), chip("Light mode ready", PALETTE.bronze)])]),
            card([text("Security", 16, ft.FontWeight.BOLD), text("Session timeout, role checks, and private-module isolation are enabled.", 13)]),
        ],
    )
