from __future__ import annotations

from pathlib import Path

import flet as ft

from ola_360.components.app_shell import shell
from ola_360.core.config import load_settings
from ola_360.core.logging_config import configure_logging
from ola_360.core.theme import PALETTE
from ola_360.repositories.app_repository import AppRepository
from ola_360.repositories.database import init_db
from ola_360.services.ai_service import AIService
from ola_360.services.auth_service import AuthService
from ola_360.services.brief_service import MorningBriefService
from ola_360.services.notification_service import NotificationService
from ola_360.services.offline_service import OfflineService
from ola_360.services.state import AppState
from ola_360.views.ai_view import ai_view
from ola_360.views.home_view import home_view
from ola_360.views.meetings_view import meetings_view
from ola_360.views.my_day_view import my_day_view
from ola_360.views.radar_view import radar_view
from ola_360.views.secondary_view import secondary_view


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = PROJECT_ROOT / "assets"


def flet_main(page: ft.Page) -> None:
    """Build one isolated OLA 360 application session."""
    settings = load_settings()
    configure_logging(settings.db_path.parents[1])
    init_db(settings.db_path)

    repo = AppRepository(settings.db_path)
    state = AppState()
    auth = AuthService(repo, settings)
    brief = MorningBriefService(repo)
    ai = AIService(repo)
    offline = OfflineService()
    notifications = NotificationService(repo)

    page.title = settings.app_name
    page.theme_mode = ft.ThemeMode.DARK
    page.window.min_width = 360
    page.window.min_height = 720
    page.bgcolor = PALETTE.bg
    page.padding = 0
    page.scroll = ft.ScrollMode.ADAPTIVE

    try:
        state.user = auth.authenticate("ola@samco.local", "Ola360!", remember_device=True)
        state.authenticated = True
        state.remember_device = True
    except Exception:
        state.authenticated = True

    def selected_content() -> ft.Control:
        if state.secondary_page:
            return secondary_view(repo, state, state.notifications, render_app)
        if state.active_tab == 0:
            return home_view(repo, brief, offline, state, render_app)
        if state.active_tab == 1:
            return radar_view(repo, state, render_app)
        if state.active_tab == 2:
            return meetings_view(repo, ai, render_app)
        if state.active_tab == 3:
            return ai_view(ai)
        return my_day_view(repo, auth, state, render_app)

    def render_app() -> None:
        state.notifications = notifications.build_notifications()
        content = selected_content()
        page.views.clear()
        page.theme_mode = (
            ft.ThemeMode.DARK
            if state.theme_mode == "dark"
            else ft.ThemeMode.LIGHT
        )
        page.views.append(
            shell(
                settings,
                state,
                content,
                on_nav,
                on_language_toggle,
                on_theme_toggle,
                on_notifications_toggle,
                on_more,
            )
        )
        page.update()

    def on_nav(e: ft.ControlEvent) -> None:
        state.active_tab = int(getattr(e.control, "selected_index", 0) or 0)
        state.secondary_page = None
        render_app()

    def on_language_toggle(e: ft.ControlEvent) -> None:
        state.language = "ar" if state.language == "en" else "en"
        render_app()

    def on_theme_toggle(e: ft.ControlEvent) -> None:
        state.theme_mode = "light" if state.theme_mode == "dark" else "dark"
        render_app()

    def on_notifications_toggle(e: ft.ControlEvent) -> None:
        state.notifications_open = not state.notifications_open
        render_app()

    def on_more(e: ft.ControlEvent) -> None:
        state.secondary_page = str(getattr(e, "data", "") or "reports")
        state.notifications_open = False
        render_app()

    render_app()


def main() -> None:
    """Run the application directly for local development."""
    ft.run(main=flet_main, assets_dir=str(ASSETS_DIR))
