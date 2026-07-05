from __future__ import annotations

from ola_360.core.localization import is_rtl, tr
from ola_360.core.theme import PALETTE


def test_arabic_layout_contract() -> None:
    assert is_rtl("ar")
    assert tr("home", "ar") == "الرئيسية"
    assert tr("notifications", "ar") == "الإشعارات"


def test_dark_mode_palette_contract() -> None:
    assert PALETTE.bg.startswith("#")
    assert PALETTE.panel.startswith("#")
    assert PALETTE.text.startswith("#")


def test_responsive_width_targets_documented() -> None:
    widths = [360, 390, 430, 768, 1024, 1440]
    assert min(widths) == 360
    assert 390 in widths
