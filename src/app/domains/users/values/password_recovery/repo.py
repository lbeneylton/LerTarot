from datetime import datetime, timezone

from sqlalchemy import select

from app.db.contract import SessionContract
from app.domains.users.values.password_recovery.models import PasswordRecovery


class PasswordRecoveryRepo:
    def __init__(self, session: SessionContract) -> None:
        self.session = session

    # Query base apenas para recoverys ativos
    # (não usados e não expirados)
    def _active_only(self):
        return select(PasswordRecovery).where(
            PasswordRecovery.used_at.is_(None),
            PasswordRecovery.expires_at > datetime.now(timezone.utc)
            )

    # Criação de recovery
    def save(self, recovery: PasswordRecovery) -> PasswordRecovery:
        self.session.add(recovery)
        return recovery

    # Buscar provedor ativo por ID
    def get_active_by_id(self, recovery_id: int) -> PasswordRecovery | None:     
        result = self.session.execute(
            self._active_only().where(PasswordRecovery.recovery_id == recovery_id)
        ).scalar_one_or_none()
        return result

    # Invalidar todos os tokens ativos de um usuário
    def invalidate_user_tokens(self, user_id: int) -> list[PasswordRecovery]:
        recoveries = self.session.execute(
            self._active_only().where(
                PasswordRecovery.user_id == user_id
            )
        ).scalars().all()

        now = datetime.now(timezone.utc)

        for recovery in recoveries:
            recovery.used_at = now

        return list(recoveries)
    
    
    def get_active_tokens(self) -> list[PasswordRecovery]:
        result = self.session.execute(
            self._active_only()
        ).scalars().all()
        return list(result)
    
    
    
    
    def get_active_tokens_by_user(
        self,
        user_id: int,
    ) -> list[PasswordRecovery]:
        result = self.session.execute(
            self._active_only().where(
                PasswordRecovery.user_id == user_id
            )
        ).scalars().all()

        return list(result)
