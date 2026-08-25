from typing import Sequence, Any
from datetime import datetime, timezone
from sqlalchemy import select
from app.domains.users.values.providers.models import Provider


class ProviderRepo:
    def __init__(self, session: Any) -> None:
        self.session = session

    def _active_only(self):
        return select(Provider).where(Provider.deleted_at.is_(None))

    async def save(self, user: Provider) -> Provider:
        self.session.add(user)
        return user

    async def get_active_by_id(self, provider_id: int) -> Provider | None:
        result = await self.session.execute(
            self._active_only().where(Provider.provider_id == provider_id)
        )
        return result.scalar_one_or_none()

    async def get_active_by_provider(self, provider: str) -> Provider | None:
        result = await self.session.execute(
            self._active_only().where(Provider.provider == provider)
        )
        return result.scalar_one_or_none()

    async def delete(self, user_id: int) -> Provider | None:
        user = await self.get_active_by_id(user_id)
        if not user:
            return None

        user.deleted_at = datetime.now(timezone.utc)
        self.session.add(user)
        return user

    async def list_active(self) -> Sequence[Provider]:
        result = await self.session.execute(self._active_only())
        return list(result.scalars().all())
