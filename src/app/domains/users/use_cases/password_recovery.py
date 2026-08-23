# Utils e time
import secrets
from datetime import datetime, timezone, timedelta

# Classe para hashes
from app.security.hasher import Argon2Hasher

# Erros
from app.core.exceptions import (
    UnauthorizedError
)

# Modelos
from app.domains.users.values.password_recovery.models import PasswordRecovery

# UOW
from app.db.uow import SqlAlchemyUnitOfWork


# Criadores de email no outbox
from app.domains.emails.services import EmailService
from app.domains.emails.models import EmailMessage




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

    def recovery_password(self, email: str) -> None:
        """
        Solicita recuperação de senha.

        Se o usuário existir:
        - invalida tokens anteriores;
        - gera um novo token;
        - salva apenas o hash do token;
        - define validade de 15 minutos;
        - cria uma mensagem no outbox.

        Se o usuário não existir, retorna normalmente para
        não revelar se o e-mail está cadastrado.
        """

        with self.uow as uow:
            user = uow.users.get_active_by_email(email)

            # Não revela se o e-mail existe.
            if user is None:
                return
            
            # Invalida recuperações anteriores.
            uow.password_recovery.invalidate_user_tokens(
                user.user_id
            )

            # Token puro.
            token = secrets.token_urlsafe(32)

            # Expitra em 15 minutos.
            expires_at = (
                datetime.now(timezone.utc)
                + timedelta(minutes=15)
            )

            # Apenas o hash vai para o banco.
            token_hash = self.hasher.hash(token)

            recovery = PasswordRecovery(
                user_id=user.user_id,
                token_hash=token_hash,
                expires_at=expires_at,
            )

            uow.password_recovery.save(recovery)


            idempotency_key = (
                f"recovery_password:"
                f"{user.user_id}:"
                f"{token_hash}"
            )
            
            email_message= EmailMessage(
                idempotency_key=idempotency_key,
                to=user.email,
                subject="Solicitação de alteração de senha",
                body="password_reset",
                variables={
                    "user_name": user.username,
                    "token": token
                }
            )

            uow.emails.save(email_message)
                         

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
            
            now = datetime.now(timezone.utc)

            for recovery in recoveries:

                # Token expirado.
                if recovery.expires_at <= now:
                    continue
                
                # Confere o token puro contra o hash.
                if not self.hasher.verify_hash(
                    token,
                    recovery.token_hash,
                ):
                    continue


                # Confere se o usuário ainda está ativo.
                user = uow.users.get_active_by_id(
                    recovery.user_id
                )

                if user is None:
                    raise UnauthorizedError(
                        "Token inválido"
                    )

                 # Altera a senha.
                user.password_hash = self.hasher.hash(
                    new_password
                )


                # Invalida o token após utilização.
                recovery.used_at = now
                return 

            raise UnauthorizedError(
                "Token de recuperação inválido ou expirado"
            )


    # Inuteis

    # def change_password(
    #     self,
    #     user: User,
    #     current_password: str,
    #     new_password: str,
    # ) -> str:
    #     """
    #     Altera a senha de um usuário autenticado.

    #     Diferentemente do reset_password(), aqui o usuário
    #     precisa informar a senha atual.
    #     """

    #     if not self.hasher.verify_hash(
    #         current_password,
    #         user.password_hash,
    #     ):
    #         raise UnauthorizedError(
    #             "Senha atual inválida"
    #         )

    #     if current_password == new_password:
    #         raise ConflictError(
    #             "A nova senha deve ser diferente da senha atual"
    #         )

    #     with self.uow as uow:
    #         user.password_hash = self.hasher.hash(
    #             new_password
    #         )

    #         uow.users.save(user)

    #         # Opcional: invalida tokens de recuperação
    #         # que ainda estejam ativos.
    #         uow.password_recovery.invalidate_user_tokens(
    #             user.user_id
    #         )

    #     return "Senha alterada"
 
        """
        Valida o token de recuperação.

        Não altera a senha.
        Apenas confirma que o token:
        - existe;
        - não expirou;
        - não foi utilizado;
        - pertence a um usuário ativo.
        """

        with self.uow as uow:

            recoveries = (
                uow.password_recovery.get_active_tokens()
            )

            now = datetime.now(timezone.utc)

            for recovery in recoveries:

                # Token já expirado.
                if recovery.expires_at <= now:
                    continue

                # Confere token puro contra hash.
                if not self.hasher.verify_hash(
                    token,
                    recovery.token_hash,
                ):
                    continue

                # Confere se o usuário ainda existe.
                user = uow.users.get_active_by_id(
                    recovery.user_id
                )

                if user is None:
                    raise UnauthorizedError(
                        "Token inválido"
                    )

                # Token válido.
                return True

            raise UnauthorizedError(
                "Token de recuperação inválido ou expirado"
            )