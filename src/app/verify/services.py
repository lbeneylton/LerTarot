
from app.users.models import User
from app.verify.models import CodeEmailVerificator


from app.db.uow import SqlAlchemyUnitOfWork

from app.security.hasher import Argon2Hasher
from app.verify.sender import EmailSender

from app.core.exceptions import VerificationError

from datetime import datetime, timedelta, timezone
import secrets


class VerificatorEmailService:
    def __init__(
        self, 
        uow: SqlAlchemyUnitOfWork,
        hasher: Argon2Hasher,
        email_sender: EmailSender, 
    ) -> None:        
        self.email_code_repo = email_code_repo
        self.user_repo = user_repo
        self.email_sender = email_sender
        self.hasher = hasher
        
          
    def _validar_se_email_verificado(user: User) -> None:
        if user.email_verified:
            raise VerificationError(
                "Email já verificado"
            )


    def _validar_verificacao(verification:CodeEmailVerificator):
        # Verifica se o codigo existe 
        if not verification:
            raise VerificationError(
                "Código inválido",
            )
            
        # Verifica se o código já foi utilizado   
        if verification.used:
            raise VerificationError(
                "Código já utilizado",
            )

        # Verifica expiração
        now = datetime.now(timezone.utc)
        if verification.expires_at <= now:
            raise VerificationError(
                "Tempo expirado",
            )

        # Verifica tentativas máximas
        if verification.attempts >= 5:
            raise VerificationError(
                "Tentativas demais, expirado",
            )
            
        
    def send_code(self, user: User):
        """Envia codigo pro email do usuario"""
        
        # Invalida códigos antigos
        self.email_code_repo.invalidate_user_codes(user.user_id)
        
        # Gerar novo código e hashear
        code = f"{secrets.randbelow(1_000_000):06d}"
        code_hash  = self.hasher.hash(str(code))

        # Gera um prazo
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=15
        )

        # Criar um CodeEmailVerificator
        verification = CodeEmailVerificator(
            user_id=user.user_id,
            code_hash=code_hash,
            expires_at=expires_at,
        )

        # Persiste um CodeEmailVerificator
        self.email_code_repo.session.add(verification)
        self.email_code_repo.session.commit()
        self.email_code_repo.session.refresh(verification)

        # Envia o email
        self.email_sender.send(
            to=user.email,
            subject="Verifique seu email",
            body=f"Seu código de verificação é: {code}",
        )


    def verify_code(self, user: User, code: str):
        """Verifica o codigo do usuário"""
        
        # Verifica se está com email verificado
        self._validar_se_email_verificado(user)
        
        # Busca o ultimo código ativo do usuário
        verification = self.email_code_repo.get_latest_active(user.user_id)

        # Valida a verificação
        self._validar_verificacao(verification)

        # Adiciona uma tentativa
        verification.attempts += 1

        # Verifica se o codigo está correto
        if not self.hasher.verify_hash(
            code,
            verification.code_hash,
        ):
            self.email_code_repo.save(verification)
            self.email_code_repo.session.commit()
            self.email_code_repo.session.refresh(verification)
            raise VerificationError(
                "Código Inválido",
            )
        

        verification.used_at = now
        user.email_verified = True

        
        self.user_repo.save(user)
        self.email_code_repo.save(verification)
        
        self.user_repo.session.flush()
        self.email_code_repo.session.flush()
        
        self.user_repo.session.refresh(user)
        self.email_code_repo.session.refresh(verification)

        return user
