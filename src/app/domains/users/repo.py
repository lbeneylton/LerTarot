from datetime import datetime, timezone

from sqlalchemy import select
from app.db.contract import SessionContract

from app.domains.users.models import User
from typing import Sequence


class UserRepo:
    def __init__(self, session: SessionContract) -> None:
        self.session = session

    # Criação de usuário polimórfico
    def save(self, user: User) -> User:
        self.session.add(user)
        return user

    # Buscar usuário ativo por UUID
    def get_active_by_id(self, user_id: int) -> User | None:
        stmt = (
            select(User)
            .where(
                User.user_id == user_id,
                User.deleted_at.is_(None)
            )
        )
        return self.session.execute(stmt).scalar_one_or_none()
        

    # Buscar usuário ativo por email
    def get_active_by_email(self, email: str) -> User | None:
        return self.session.execute(
            select(User)
            .where(
                User.deleted_at.is_(None),
                User.email == email
            )
        ).scalar_one_or_none()

    # Buscar usuário ativo por username
    def get_active_by_username(self, username: str) -> User | None:
        return self.session.execute(
            select(User)
            .where(
                User.username == username,
                User.deleted_at.is_(None)
            )
        ).scalar_one_or_none()
        

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
        return self.session.execute(
            select(User)
            .where(User.deleted_at.is_(None))
        ).scalars().all()
        
