from __future__ import annotations

from ola_360.core.config import Settings
from ola_360.core.security import verify_password
from ola_360.models.entities import User
from ola_360.repositories.app_repository import AppRepository


class AuthService:
    def __init__(self, repo: AppRepository, settings: Settings):
        self.repo = repo
        self.settings = settings

    def authenticate(self, email: str, password: str, remember_device: bool = False) -> User:
        row = self.repo.get_user_by_email(email.strip().lower())
        if not row or not verify_password(password, row["password_hash"]):
            raise ValueError("Invalid email or password")
        return User(id=row["id"], name=row["name"], email=row["email"], role=row["role"])

    def can_access_private(self, user: User | None) -> bool:
        return bool(user and user.role == "Executive")
