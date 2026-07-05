from __future__ import annotations

from dataclasses import dataclass, field

from ola_360.models.entities import User


@dataclass
class AppState:
    user: User | None = None
    authenticated: bool = False
    remember_device: bool = False
    selected_sector: str = "All"
    selected_project: str = "All"
    warning_severity: str = "All"
    theme_mode: str = "dark"
    language: str = "en"
    offline: bool = False
    private_unlocked: bool = False
    active_tab: int = 0
    secondary_page: str | None = None
    notifications: list[str] = field(default_factory=list)
    notifications_open: bool = False

    def logout(self) -> None:
        self.user = None
        self.authenticated = False
        self.private_unlocked = False
        self.notifications_open = False
        self.secondary_page = None
