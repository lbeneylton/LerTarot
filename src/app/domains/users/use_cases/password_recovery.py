import secrets
from datetime import datetime, timezone, timedelta

from app.security.hasher import Argon2Hasher
from app.core.exceptions import UnauthorizedError
from app.domains.users.values.password_recovery.models import PasswordRecovery
from app.db.uow import SqlAlchemyUnitOfWork
from app.domains.emails.services import EmailService
from app.domains.emails.models import EmailMessage
from app.core.config import settings


class PasswordRecoveryUseCase:
    def __init__(
        self,
        uow: SqlAlchemyUnitOfWork,
        hasher: Argon2Hasher,
        email_sender: EmailService 
    ) -> None:
        self.uow = uow
        self.hasher = hasher
        self.email_sender = email_sender

    async def recovery_password(self, email: str) -> None:
        """Solicita recuperação de senha e gera o e-mail no outbox com o template password_reset."""
        async with self.uow as uow:
            user = await uow.users.get_active_by_email(email)

            if user is None:
                return

            await uow.password_recovery.invalidate_user_tokens(user.user_id)

            token = secrets.token_urlsafe(32)
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
            token_hash = self.hasher.hash(token)

            recovery = PasswordRecovery(
                user_id=user.user_id,
                token_hash=token_hash,
                expires_at=expires_at,
            )

            await uow.password_recovery.save(recovery)

            idempotency_key = f"recovery_password:{user.user_id}:{token_hash}"
            
            email_message = EmailMessage(
                idempotency_key=idempotency_key,
                to=user.email,
                subject="Solicitação de alteração de senha",
                template="password_reset",
                body="password_reset",
                variables={
                    "user_name": user.username or "Usuário",
                    "url_reset": str(settings.url_recovery_password),
                    "token": token,
                    "year": datetime.now(timezone.utc).year
                }
            )

            await uow.emails.save(email_message)

    async def reset_password(self, token: str, new_password: str) -> None:
        """Redefine a senha utilizando o token recebido."""
        async with self.uow as uow:
            recoveries = await uow.password_recovery.get_active_tokens()
            now = datetime.now(timezone.utc)

            for recovery in recoveries:
                if recovery.expires_at <= now:
                    continue

                if not self.hasher.verify_hash(token, recovery.token_hash):
                    continue

                user = await uow.users.get_active_by_id(recovery.user_id)
                if user is None:
                    raise UnauthorizedError("Token inválido")

                user.password_hash = self.hasher.hash(new_password)
                recovery.used_at = now
                await uow.users.save(user)
                await uow.password_recovery.save(recovery)
                return

            raise UnauthorizedError("Token de recuperação inválido ou expirado")