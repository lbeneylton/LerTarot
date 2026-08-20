from datetime import datetime, timezone

from sqlalchemy import select
from app.db.contract import SessionContract

from app.users.models import User
from typing import Sequence


class UserRepo:
    def __init__(self, session: SessionContract) -> None:
        self.session = session

    # Query base apenas para usuários ativos
    def _active_only(self):
        return select(User).where(User.deleted_at.is_(None))

    # Criação de usuário polimórfico
    def save(self, user: User) -> User:
        self.session.add(user)
        return user

    # Buscar usuário ativo por UUID
    def get_active_by_id(self, user_id: int) -> User | None:
        result = self.session.execute(
            self._active_only().where(User.user_id == user_id)
        ).scalar_one_or_none()
        return result

    # Buscar usuário ativo por email
    def get_active_by_email(self, email: str) -> User | None:
        result = self.session.execute(
            self._active_only().where(User.email == email)
        ).scalar_one_or_none()
        return result

    # Buscar usuário ativo por username
    def get_active_by_username(self, username: str) -> User | None:
        result = self.session.execute(
            self._active_only().where(User.username == username)
        ).scalar_one_or_none()
        return result

    # Soft delete
    def delete(self, user_id: int) -> User | None:
        user = self.get_active_by_id(user_id)
        if not user:
            return None

        user.deleted_at = datetime.now(timezone.utc)
        self.session.add(user)
        return user

    # Buscar todos os usuários ativos
    def list_active(self) -> Sequence[User]:
        result = self.session.execute(
            self._active_only()
        ).scalars().all()
        return result
