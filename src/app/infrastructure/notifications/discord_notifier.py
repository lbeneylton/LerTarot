import httpx
import asyncio
import logging
from typing import Any

from app.core.config import settings
from app.core.contracts.notification import NotificationContract

logger = logging.getLogger(__name__)

class DiscordNotifier(NotificationContract):
    """Implementação concreta de NotificationContract enviando para Webhooks do Discord."""

    def __init__(self) -> None:
        self.webhook_users = settings.discord_webhook.url_users
        self.webhook_emails = settings.discord_webhook.url_emails

    async def notify_new_user(self, user_name: str, user_email: str) -> None:
        if not self.webhook_users:
            return

        payload = {
            "embeds": [
                {
                    "title": "🎉 Novo Usuário Cadastrado!",
                    "description": f"O usuário **{user_name}** ({user_email}) acabou de se registrar na plataforma.",
                    "color": 3066993, # Verde
                }
            ],
            "username": "LerTarot Auditor",
        }
        await self._send_async(self.webhook_users, payload)

    async def notify_email_sent(self, to_email: str, subject: str) -> None:
        if not self.webhook_emails:
            return

        payload = {
            "embeds": [
                {
                    "title": "📧 E-mail Enviado com Sucesso",
                    "description": f"Destinatário: `{to_email}`\nAssunto: `{subject}`",
                    "color": 3447003, # Azul
                }
            ],
            "username": "LerTarot Auditor",
        }
        await self._send_async(self.webhook_emails, payload)

    async def _send_async(self, webhook_url: str, payload: dict[str, Any]) -> None:
        """Dispara a requisição HTTP em background task para não bloquear o fluxo."""
        loop = asyncio.get_running_loop()
        loop.create_task(self._fire_and_forget(webhook_url, payload))

    async def _fire_and_forget(self, webhook_url: str, payload: dict[str, Any]) -> None:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(webhook_url, json=payload, timeout=5.0)
        except Exception as e:
            logger.error(f"Falha ao enviar notificação de negócio para o Discord: {e}")
