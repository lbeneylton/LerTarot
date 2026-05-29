from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.users.models import User
from typing import Sequence


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # Query base apenas para usuários ativos
    def _active_only(self):
        return select(User).where(User.deleted_at.is_(None))

    # Criação de usuário polimórfico
    def create(self, user: User) -> User:
        self.session.add(user)
        return user

    # Buscar usuário ativo por UUID
    def get_active_by_id(self, user_id: UUID) -> User | None:
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

    # Atualização genérica (merge/add)
    # def update(self, user: User) -> User:
    #     self.session.add(user)
    #     return user

    # Soft delete
    def delete(self, user_id: UUID) -> User | None:
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
