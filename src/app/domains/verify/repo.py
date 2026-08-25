from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select, update
from app.domains.verify.models import CodeEmail


class CodeEmailRepo:
    def __init__(self, session: Any) -> None:
        self.session = session

    async def save(self, verification: CodeEmail) -> CodeEmail:
        self.session.add(verification)
        return verification

    async def invalidate_user_codes(self, user_id: int) -> None:
        now = datetime.now(timezone.utc)
        stmt = (
            update(CodeEmail)
            .where(
                CodeEmail.user_id == user_id,
                CodeEmail.used_at.is_(None)
            )
            .values(used_at=now)
        )
        await self.session.execute(stmt)

    async def get_latest_active(self, user_id: int) -> CodeEmail | None:
        now = datetime.now(timezone.utc)
        stmt = (
            select(CodeEmail)
            .where(
                CodeEmail.user_id == user_id,
                CodeEmail.used_at.is_(None),
                CodeEmail.expires_at > now
            )
            .order_by(CodeEmail.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exist_this_code_active(self, user_id: int, code_hash: str) -> bool:
        now = datetime.now(timezone.utc)
        stmt = (
            select(CodeEmail)
            .where(
                CodeEmail.user_id == user_id,
                CodeEmail.code_hash == code_hash,
                CodeEmail.used_at.is_(None),
                CodeEmail.expires_at > now
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None