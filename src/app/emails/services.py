
from app.users.models import User
from app.users.repo import UserRepo

from app.emails.models import EmailVerificationCode
from app.emails.repo import EmailVerificationRepo

from app.security.hasher import Argon2Hasher
from app.emails.sender import EmailSender

from app.core.exceptions import VerificationError

from datetime import datetime, timedelta, timezone
import secrets


class EmailVerificationService:
    def __init__(
        self, 
        email_code_repo:EmailVerificationRepo , 
        user_repo: UserRepo, 
        hasher: Argon2Hasher,
        email_sender: EmailSender, 
    ) -> None:
        self.email_code_repo = email_code_repo
        self.user_repo = user_repo
        self.email_sender = email_sender
        self.hasher = hasher

    def send_code(self, user: User):
        # Inválida codigos anteriores e gera um novo
        self.email_code_repo.invalidate_user_codes(user.user_id)
        code = f"{secrets.randbelow(1_000_000):06d}"
        code_hash  = self.hasher.hash(str(code))

        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=15
        )

        verification = EmailVerificationCode(
            user_id=user.user_id,
            code_hash=code_hash,
            expires_at=expires_at,
        )

        self.email_code_repo.session.add(verification)
        self.email_code_repo.session.commit()
        self.email_code_repo.session.refresh(verification)

        self.email_sender.send(
            to=user.email,
            subject="Verifique seu email",
            body=f"Seu código de verificação é: {code}",
        )


    def verify_code(self, user: User, code: str):
        if user.email_verified:
            raise VerificationError(
                "Email já verificado"
            )
        
        # Busca código ativo do usuário
        verification = self.email_code_repo.get_latest_active(user.user_id)

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
        self.user_repo.session.commit()
        self.user_repo.session.refresh(user)
        
        
        self.email_code_repo.save(verification)
        self.email_code_repo.session.commit()
        self.email_code_repo.session.refresh(verification)

        return user
