# Classe para hashes
from app.security.hasher import Argon2Hasher

# Erros
from app.core.exceptions import (
    UnauthorizedError,
    ConflictError,
    NotFoundError
)

# Tipos e modelos
from app.domains.users.models import User

# UOW
from app.db.uow import SqlAlchemyUnitOfWork


# Verificador de email
from app.domains.verify.services import CodeEmailService


import secrets
from datetime import datetime, timezone, timedelta


   

class PasswordService:
    def __init__(self, uow, hasher: Argon2Hasher, email_sender: CodeEmailService) -> None:
        self.uow = uow
        self.hasher = hasher
        self.email_sender = email_sender
        

    def recovery_password(self, email: str) -> None:
        """
        Solicita recuperação de senha.

        Gera um token temporário e envia para o e-mail.
        """

        with self.uow as uow:
            # Verifica se existe um usuario para esse email
            user = uow.users.get_active_by_email(email)

            # Usuário não encontrado
            if user is None:
                raise NotFoundError("Usuário não encontrado")

            # Invalida tokens anteriores
            uow.password_reset_repo.invalidate_user_tokens(user.id)

            # Gera token seguro
            token = secrets.token_urlsafe(32)

            # Validade de 15 minutos
            expires_at = (
                datetime.now(timezone.utc)
                + timedelta(minutes=15)
            )

            # Não salvar o token puro
            token_hash = self.hasher.hash(token)

            uow.password_reset_repo.create(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=expires_at,
                used=False,
            )

            uow.password_reset_repo.session.flush()

            # Envia o token/link por e-mail
            self.email_sender.send_code(
                user
            )

            return None

    #
    # Password
    #
    def reset_password(
        self,
        token: str,
        new_password: str,
    ) -> None:
        """
        Redefine a senha usando um token de recuperação.
        """

        reset = self.uow.password_reset_repo.get_active_tokens()

        now = datetime.now(timezone.utc)

        for item in reset:
            if item.used:
                continue

            if item.expires_at <= now:
                continue

            if self.hasher.verify_hash(
                token,
                item.token_hash,
            ):
                user = self.uow.get_by_id(item.user_id)

                if user is None:
                    raise UnauthorizedError(
                        "Token inválido"
                    )

                user.password_hash = (
                    self.hasher.hash(new_password)
                )

                # Token só pode ser utilizado uma vez
                item.used = True

                self.uow.save(user)
                self.uow.password_reset_repo.save(item)

                self.uow.session.flush()

                return None

        raise UnauthorizedError(
            "Token de recuperação inválido ou expirado"
        )

    def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> str:
        """
        Altera a senha de um usuário autenticado.
        """

        if not self.hasher.verify_hash(
            current_password,
            user.password_hash,
        ):
            raise UnauthorizedError(
                "Senha atual inválida"
            )

        if current_password == new_password:
            raise ConflictError(
                "A nova senha deve ser diferente da senha atual"
            )

        user.password_hash = self.hasher.hash(
            new_password
        )

        self.uow.save(user)
        self.uow.session.flush()
        self.uow.session.refresh(user)
        
        return "Senha alterada"


 
 
 
 
#  PasswordResetToken
# ------------------
# id
# user_id
# token_hash
# expires_at
# used_at
# created_at