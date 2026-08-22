from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.providers.models import Provider
from typing import Sequence


class ProviderRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # Query base apenas para provedores ativos
    def _active_only(self):
        return select(Provider).where(Provider.deleted_at.is_(None))

    # Criação de provedor polimórfico
    def save(self, user: Provider) -> Provider:
        self.session.add(user)
        return user

    # Buscar provedor ativo por UUID
    def get_active_by_id(self, provider_id: UUID) -> Provider | None:
        result = self.session.execute(
            self._active_only().where(Provider.provider_id == provider_id)
        ).scalar_one_or_none()
        return result

    # Buscar provedor ativo por provider
    def get_active_by_provider(self, provider: str) -> Provider | None:
        result = self.session.execute(
            self._active_only().where(Provider.provider == provider)
        ).scalar_one_or_none()
        return result

    # Atualização genérica (merge/add)
    # def update(self, user: Provider) -> Provider:
    #     self.session.add(user)
    #     return user

    # Soft delete

    def delete(self, user_id: UUID) -> Provider | None:
        user = self.get_active_by_id(user_id)
        if not user:
            return None

        user.deleted_at = datetime.now(timezone.utc)
        self.session.add(user)
        return user

    # Buscar todos os usuários ativos
    def list_active(self) -> Sequence[Provider]:
        result = self.session.execute(
            self._active_only()
        ).scalars().all()
        return result
