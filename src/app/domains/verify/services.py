from datetime import datetime, timezone, timedelta
import secrets

from app.domains.users.models import User
from app.domains.verify.models import CodeEmail
from app.db.uow import SqlAlchemyUnitOfWork
from app.security.hasher import Argon2Hasher
from app.core.exceptions import VerificationError

from emails.model import EmailMessage, MessageStatus


class CodeEmailService:
    def __init__(
        self, 
        uow: SqlAlchemyUnitOfWork,
        hasher: Argon2Hasher,
    ) -> None:        
        self.uow = uow
        self.hasher = hasher
        
        self.email_code_repo = uow.email_codes
        self.user_repo = uow.users

    def _validar_se_email_verificado(self, user: User) -> None:
        if user.email_verified:
            raise VerificationError("Email já verificado")

    def _validar_verificacao(self, verification: CodeEmail) -> None:
            
        # Verifica se o código já foi utilizado   
        if verification.used_at is not None:
            raise VerificationError("Código já utilizado")

        # Verifica expiração
        now = datetime.now(timezone.utc)
        if verification.expires_at <= now:
            raise VerificationError("Tempo expirado")

        # Verifica tentativas máximas
        if verification.attempts >= 5:
            raise VerificationError("Tentativas demais, expirado")

    def send_code(self, user: User) -> None:
        """Gera e persiste o código de verificação, salvando o e-mail no outbox."""
        with self.uow as uow:
            # Invalida códigos antigos
            uow.email_codes.invalidate_user_codes(user.user_id)
            
            # Gerar novo código e hashear (6 dígitos)
            code = f"{secrets.randbelow(1_000_000):06d}"
            code_hash = self.hasher.hash(str(code))

            # Gera um prazo (15 minutos)
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

            # Criar um CodeEmail
            verification = CodeEmail(
                user_id=user.user_id,
                code_hash=code_hash,
                expires_at=expires_at,
            )

            # Persiste o código
            uow.email_codes.save(verification)
            
            # Enfileira o e-mail na fila (outbox) de forma transacional e idempotente
            idempotency_key = f"verify_email:{user.user_id}:{code_hash}"
            email_message = EmailMessage(
                idempotency_key=idempotency_key,
                to=user.email,
                subject="Verifique seu e-mail - Ler Tarot",
                body=f"Seu código de verificação é: {code}",
                status=MessageStatus.PENDING
            )
            uow.emails.save(email_message)

    def verify_code(self, user: User, code: str) -> User:
        """Verifica o codigo do usuário"""
        with self.uow as uow:
            # Verifica se está com email verificado
            self._validar_se_email_verificado(user)
            
            # Busca o ultimo código ativo do usuário
            verification = uow.email_codes.get_latest_active(user.user_id)
            
            # Verifica se o código existe 
            if not verification:
                raise VerificationError("Código não encontrado")
            
            # Valida a verificação
            self._validar_verificacao(verification)

            # Adiciona uma tentativa
            verification.attempts += 1

            # Verifica se o codigo está correto
            if not self.hasher.verify_hash(code, verification.code_hash):
                uow.email_codes.save(verification)
                raise VerificationError("Código Inválido")

            now = datetime.now(timezone.utc)
            verification.used_at = now
            user.email_verified = True

            uow.users.save(user)
            uow.email_codes.save(verification)

            return user
