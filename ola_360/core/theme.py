from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    bg: str = "#121018"
    panel: str = "#1C1824"
    panel_2: str = "#252031"
    text: str = "#F8F4EE"
    muted: str = "#B9AFBF"
    plum: str = "#7A2D5C"
    aubergine: str = "#3B1836"
    bronze: str = "#C99A52"
    emerald: str = "#2E9D78"
    amber: str = "#D8A53C"
    red: str = "#B9404D"
    blue: str = "#6E8FB8"
    border: str = "#3A3145"
    ivory: str = "#FFF8EC"


PALETTE = Palette()


def severity_color(severity: str) -> str:
    return {
        "Information": PALETTE.blue,
        "Watch": PALETTE.amber,
        "Intervention": PALETTE.plum,
        "Critical": PALETTE.red,
    }.get(severity, PALETTE.muted)
