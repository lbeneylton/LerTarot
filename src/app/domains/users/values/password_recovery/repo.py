from datetime import datetime, timezone

from sqlalchemy import select, update

from app.db.contract import SessionContract
from app.domains.users.values.password_recovery.models import PasswordRecovery


class PasswordRecoveryRepo:
    def __init__(self, session: SessionContract) -> None:
        self.session = session

    # Criação de recovery
    def save(self, recovery: PasswordRecovery) -> PasswordRecovery:
        self.session.add(recovery)
        return recovery

    # Buscar provedor ativo por ID
    def get_active_by_id(self, recovery_id: int) -> PasswordRecovery | None: 
        stmt = (
            select(PasswordRecovery)
            .where(
                PasswordRecovery.recovery_id == recovery_id,
                PasswordRecovery.used_at.is_(None),
                PasswordRecovery.expires_at > datetime.now(timezone.utc)
            )
        )
        return self.session.execute(stmt).scalar_one_or_none()

    # Invalidar todos os tokens ativos de um usuário
    def invalidate_user_tokens(self, user_id: int) -> None:
        now = datetime.now(timezone.utc)
        stmt =(
            update(PasswordRecovery)
            .where(
                PasswordRecovery.user_id == user_id,
                PasswordRecovery.used_at.is_(None),
                PasswordRecovery.expires_at > datetime.now(timezone.utc)
            )
            .values(used_at=now)
        )
        self.session.execute(stmt)

    
    def get_active_tokens(self) -> list[PasswordRecovery]:
        stmt = (
            select(PasswordRecovery)
            .where(
                PasswordRecovery.used_at.is_(None),
                PasswordRecovery.expires_at > datetime.now(timezone.utc)
            )
        )
        return list(self.session.execute(stmt).scalars().all())
        
    
    def get_active_tokens_by_user(
        self,
        user_id: int,
    ) -> list[PasswordRecovery]:
        stmt = (
            select(PasswordRecovery)
            .where(
                PasswordRecovery.user_id == user_id,
                PasswordRecovery.used_at.is_(None),
                PasswordRecovery.expires_at > datetime.now(timezone.utc)
            )
        )
        return list(self.session.execute(stmt).scalars().all())
