from __future__ import annotations

import flet as ft

from ola_360.core.localization import tr
from ola_360.core.theme import PALETTE


DESTINATIONS = [
    ("home", ft.Icons.HOME_ROUNDED),
    ("radar", ft.Icons.RADAR_ROUNDED),
    ("meetings", ft.Icons.EVENT_NOTE_ROUNDED),
    ("ai", ft.Icons.AUTO_AWESOME_ROUNDED),
    ("my_day", ft.Icons.LOCK_PERSON_ROUNDED),
]


def bottom_navigation(selected: int, on_change, language: str = "en") -> ft.NavigationBar:
    return ft.NavigationBar(
        selected_index=selected,
        on_change=on_change,
        bgcolor=PALETTE.panel,
        indicator_color=PALETTE.plum,
        destinations=[
            ft.NavigationBarDestination(icon=icon, selected_icon=icon, label=tr(label, language))
            for label, icon in DESTINATIONS
        ],
    )
