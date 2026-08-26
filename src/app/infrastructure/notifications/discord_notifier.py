import httpx
import asyncio
import logging
from typing import Any

from app.core.config import settings
from app.core.contracts.notification import NotificationContract

logger = logging.getLogger(__name__)

class DiscordNotifier(NotificationContract):
    """Implementação concreta de NotificationContract enviando para Webhooks do Discord."""

    @property
    def webhook_users(self) -> str:
        return settings.discord_webhook.url_users

    @property
    def webhook_emails(self) -> str:
        return settings.discord_webhook.url_emails or self.webhook_users

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
        """Dispara a requisição HTTP para o Discord."""
        await self._fire_and_forget(webhook_url, payload)

    async def _fire_and_forget(self, webhook_url: str, payload: dict[str, Any]) -> None:
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(webhook_url, json=payload, timeout=5.0)
                if res.status_code >= 400:
                    logger.error(f"Discord Webhook retornou HTTP {res.status_code}: {res.text}")
                else:
                    logger.info(f"Notificação enviada ao Discord com sucesso! (HTTP {res.status_code})")
        except Exception as e:
            logger.error(f"Falha ao enviar notificação de negócio para o Discord: {e}")
