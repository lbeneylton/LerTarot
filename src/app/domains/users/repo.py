from datetime import datetime, timezone
from typing import Sequence, Any
from sqlalchemy import select

from app.domains.users.models import User


class UserRepo:
    def __init__(self, session: Any) -> None:
        self.session = session

    async def save(self, user: User) -> User:
        self.session.add(user)
        return user

    async def get_active_by_id(self, user_id: int) -> User | None:
        stmt = (
            select(User)
            .where(
                User.user_id == user_id,
                User.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_by_email(self, email: str) -> User | None:
        stmt = (
            select(User)
            .where(
                User.deleted_at.is_(None),
                User.email == email
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_by_username(self, username: str) -> User | None:
        stmt = (
            select(User)
            .where(
                User.username == username,
                User.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, user_id: int) -> User | None:
        user = await self.get_active_by_id(user_id)
        if not user:
            return None

        user.deleted_at = datetime.now(timezone.utc)
        self.session.add(user)
        return user

    async def list_active(self) -> Sequence[User]:
        stmt = select(User).where(User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
