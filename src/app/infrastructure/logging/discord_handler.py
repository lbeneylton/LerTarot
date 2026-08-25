import logging
import httpx
import asyncio
from typing import Any

from app.core.config import settings

class DiscordWebhookHandler(logging.Handler):
    """Logging Handler para enviar logs de nível ERROR/CRITICAL para um Discord Webhook.
    
    Usa asyncio.create_task para não bloquear a thread principal da aplicação
    durante a requisição HTTP.
    """

    def emit(self, record: logging.LogRecord) -> None:
        if not settings.discord_webhook_url:
            return

        # Formata a mensagem do log
        log_msg = self.format(record)
        
        # Prepara a carga útil (payload) para o Discord
        payload = {
            "content": None,
            "embeds": [
                {
                    "title": f"🚨 Alerta do Sistema: {record.levelname}",
                    "description": f"```python\n{log_msg[:4000]}\n```",  # Limite do Discord é 4096
                    "color": 16711680 if record.levelno >= logging.ERROR else 16753920,
                    "footer": {
                        "text": f"Logger: {record.name} | Path: {record.pathname}:{record.lineno}"
                    }
                }
            ],
            "username": "LerTarot Bot",
        }

        # Cria a tarefa assíncrona para disparar a request
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._send_async(payload))
        except RuntimeError:
            # Se não houver event loop (ex: script síncrono), roda sincronicamente
            httpx.post(settings.discord_webhook_url, json=payload, timeout=5.0)

    async def _send_async(self, payload: dict[str, Any]) -> None:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(settings.discord_webhook_url, json=payload, timeout=5.0)
        except Exception as e:
            # Não podemos logar isso novamente com o mesmo logger para evitar loops infinitos
            print(f"Falha ao enviar webhook do Discord: {e}")
