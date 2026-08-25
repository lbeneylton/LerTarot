from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select, update

from app.domains.users.values.password_recovery.models import PasswordRecovery


class PasswordRecoveryRepo:
    def __init__(self, session: Any) -> None:
        self.session = session

    async def save(self, recovery: PasswordRecovery) -> PasswordRecovery:
        self.session.add(recovery)
        return recovery

    async def get_active_by_id(self, recovery_id: int) -> PasswordRecovery | None: 
        stmt = (
            select(PasswordRecovery)
            .where(
                PasswordRecovery.recovery_id == recovery_id,
                PasswordRecovery.used_at.is_(None),
                PasswordRecovery.expires_at > datetime.now(timezone.utc)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def invalidate_user_tokens(self, user_id: int) -> None:
        now = datetime.now(timezone.utc)
        stmt = (
            update(PasswordRecovery)
            .where(
                PasswordRecovery.user_id == user_id,
                PasswordRecovery.used_at.is_(None),
                PasswordRecovery.expires_at > datetime.now(timezone.utc)
            )
            .values(used_at=now)
        )
        await self.session.execute(stmt)

    async def get_active_tokens(self) -> list[PasswordRecovery]:
        stmt = (
            select(PasswordRecovery)
            .where(
                PasswordRecovery.used_at.is_(None),
                PasswordRecovery.expires_at > datetime.now(timezone.utc)
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_tokens_by_user(self, user_id: int) -> list[PasswordRecovery]:
        stmt = (
            select(PasswordRecovery)
            .where(
                PasswordRecovery.user_id == user_id,
                PasswordRecovery.used_at.is_(None),
                PasswordRecovery.expires_at > datetime.now(timezone.utc)
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
