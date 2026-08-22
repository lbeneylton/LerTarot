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
from app.domains.users.values.password_recovery.models import PasswordRecovery

# UOW
from app.db.uow import SqlAlchemyUnitOfWork


# Verificador de email
from app.domains.verify.services import CodeEmailService


import secrets
from datetime import datetime, timezone, timedelta


from datetime import datetime, timedelta, timezone
import secrets

from app.core.exceptions import (
    ConflictError,
    UnauthorizedError,
)

from app.db.uow import SqlAlchemyUnitOfWork
from app.domains.users.models import User
from app.security.hasher import Argon2Hasher


class PasswordService:
    def __init__(
        self,
        uow: SqlAlchemyUnitOfWork,
        hasher: Argon2Hasher,
        email_sender: CodeEmailService,
    ) -> None:
        self.uow = uow
        self.hasher = hasher
        self.email_sender = email_sender

    def recovery_password(self, email: str) -> None:
        """
        Solicita recuperação de senha.

        Se o usuário existir:
        - invalida tokens anteriores;
        - gera um novo token;
        - salva apenas o hash do token;
        - define validade de 15 minutos;
        - envia o token por e-mail.

        Se o usuário não existir, retorna normalmente para
        não revelar se o e-mail está cadastrado.
        """

        with self.uow as uow:
            user = uow.users.get_active_by_email(email)

            if user is None:
                return

            # Invalida tokens anteriores do usuário.
            uow.password_recovery.invalidate_user_tokens(
                user.user_id
            )

            # Token puro.
            token = secrets.token_urlsafe(32)

            # Token válido por 15 minutos.
            expires_at = (
                datetime.now(timezone.utc)
                + timedelta(minutes=15)
            )

            # Nunca salvar o token puro no banco.
            token_hash = self.hasher.hash(token)

            recovery = PasswordRecovery(
                user_id=user.user_id,
                token_hash=token_hash,
                expires_at=expires_at,
            )

            uow.password_recovery.save(recovery)

            # Garante que o recovery seja enviado ao banco
            # antes do envio do e-mail.
            uow.session.flush()

            # O usuário precisa receber o TOKEN PURO.
            # O banco possui somente o hash.
            self.email_sender.send_link(
                user,
                token,
            )

    def reset_password(
        self,
        token: str,
        new_password: str,
    ) -> None:
        """
        Redefine a senha usando um token de recuperação.

        O token:
        - precisa existir;
        - não pode estar expirado;
        - não pode ter sido utilizado;
        - precisa corresponder ao hash salvo.

        Após o uso, o token é invalidado.
        """

        with self.uow as uow:
            recoveries = (
                uow.password_recovery.get_active_tokens()
            )

            for recovery in recoveries:

                # Verifica se o token recebido corresponde
                # ao hash armazenado.
                if not self.hasher.verify_hash(
                    token,
                    recovery.token_hash,
                ):
                    continue

                user = uow.users.get_active_by_id(
                    recovery.user_id
                )

                if user is None:
                    raise UnauthorizedError(
                        "Token inválido"
                    )

                # Define a nova senha.
                user.password_hash = self.hasher.hash(
                    new_password
                )

                # Token de recuperação só pode ser usado uma vez.
                recovery.used_at = datetime.now(timezone.utc)

                return

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

        Diferentemente do reset_password(), aqui o usuário
        precisa informar a senha atual.
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

        with self.uow as uow:
            user.password_hash = self.hasher.hash(
                new_password
            )

            uow.users.save(user)

            # Opcional: invalida tokens de recuperação
            # que ainda estejam ativos.
            uow.password_recovery.invalidate_user_tokens(
                user.user_id
            )

        return "Senha alterada"
