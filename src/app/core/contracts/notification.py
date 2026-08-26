from typing import Protocol

class NotificationContract(Protocol):
    """Contrato que define os métodos de envio de notificações de negócio."""

    async def notify_new_user(self, user_name: str, user_email: str) -> None:
        """Notifica o sistema sobre o cadastro de um novo usuário."""
        ...

    async def notify_email_sent(self, to_email: str, subject: str) -> None:
        """Notifica o sistema sobre o envio bem sucedido de um e-mail."""
        ...
