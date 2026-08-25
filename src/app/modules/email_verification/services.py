from datetime import datetime, timezone, timedelta
import secrets

from app.core.contracts.uow import UnitOfWorkContract
from app.core.contracts.security import PasswordHasherContract
from app.modules.users.models import User
from app.modules.email_verification.models import CodeEmail
from app.core.exceptions import VerificationError
from app.modules.emails.models import EmailMessage


class VerifyEmailService:
    def __init__(
        self, 
        uow: UnitOfWorkContract,
        hasher: PasswordHasherContract,
    ) -> None:        
        self.uow = uow
        self.hasher = hasher

    def _validar_se_email_verificado(self, user: User) -> None:
        if user.email_verified:
            raise VerificationError("Email já verificado")

    def _validar_verificacao(self, verification: CodeEmail) -> None:
        if verification.used_at is not None:
            raise VerificationError("Código já utilizado")

        now = datetime.now(timezone.utc)
        if verification.expires_at <= now:
            raise VerificationError("Tempo expirado")

        if verification.attempts >= 5:
            raise VerificationError("Tentativas demais, expirado")

    async def send_code(self, user: User) -> None:
        """Gera e persiste o código de verificação, salvando o e-mail no outbox."""
        async with self.uow as uow:
            await uow.email_codes.invalidate_user_codes(user.user_id)
            
            code = f"{secrets.randbelow(1_000_000):06d}"
            code_hash = self.hasher.hash(str(code))

            expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

            verification = CodeEmail(
                user_id=user.user_id,
                code_hash=code_hash,
                expires_at=expires_at,
            )

            await uow.email_codes.save(verification)
            
            idempotency_key = f"verify_email:{user.user_id}:{code_hash}"
            
            email_message = EmailMessage(
                idempotency_key=idempotency_key,
                to=user.email,
                subject="Verifique seu email",
                template="verify_email",
                body="verify_email",
                variables={
                    "user_name": user.username,
                    "code": code,
                    "year": datetime.now(timezone.utc).year
                }
            )
            await uow.emails.save(email_message)

    async def verify_code(self, user: User, code: str) -> User:
        """Verifica o código informado pelo usuário."""
        async with self.uow as uow:
            self._validar_se_email_verificado(user)
            
            verification = await uow.email_codes.get_latest_active(user.user_id)
            if not verification:
                raise VerificationError("Código não encontrado")
            
            self._validar_verificacao(verification)
            verification.attempts += 1

            if not self.hasher.verify_hash(code, verification.code_hash):
                await uow.email_codes.save(verification)
                raise VerificationError("Código Inválido")

            now = datetime.now(timezone.utc)
            verification.used_at = now
            user.email_verified = True

            await uow.users.save(user)
            await uow.email_codes.save(verification)
            return user
