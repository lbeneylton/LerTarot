import os
import logging
from jinja2 import Environment, FileSystemLoader

from app.db.uow import SqlAlchemyUnitOfWork
from emails.model import EmailMessage, MessageStatus
from emails.schemas import MessageRequest

logger = logging.getLogger("emails.service")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


class EmailService:
    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        self.uow = uow

    def _render_template(self, template_name: str, variables: dict) -> str:
        if not template_name.endswith(".html"):
            template_name += ".html"
        
        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        try:
            template = env.get_template(template_name)
            return template.render(**(variables or {}))
        except Exception as e:
            logger.error(f"Erro ao renderizar template {template_name}: {str(e)}")
            # Fallback amigável se o template for apenas um arquivo vazio de teste
            # ou levantar erro se for algo estrutural
            try:
                # Se o arquivo existir mas for vazio, ou se for simples
                template_path = os.path.join(TEMPLATES_DIR, template_name)
                if os.path.exists(template_path) and os.path.getsize(template_path) == 0:
                    return f"Template {template_name} vazio. Variáveis: {variables}"
            except Exception:
                pass
            raise ValueError(f"Não foi possível renderizar o template de e-mail: {str(e)}")

    def enqueue_email(self, data: MessageRequest, idempotency_key: str | None = None) -> EmailMessage:
        """Enfileira um e-mail no banco de dados (Outbox Pattern) para processamento assíncrono.
        
        Garante a idempotência caso a mesma idempotency_key seja informada.
        """
        # Se informou template, renderiza. Se não, usa o corpo direto.
        if data.template:
            body = self._render_template(data.template, data.variables or {})
        else:
            body = data.body or ""
            if not body:
                raise ValueError("É necessário fornecer o corpo ('body') ou um 'template' válido.")

        with self.uow as uow:
            # Validação de idempotência
            if idempotency_key:
                existing = uow.emails.get_by_idempotency_key(idempotency_key)
                if existing:
                    logger.info(f"Requisição de e-mail duplicada interceptada. Chave: {idempotency_key}")
                    return existing

            # Cria e-mail pendente
            email_message = EmailMessage(
                idempotency_key=idempotency_key,
                to=data.to,
                subject=data.subject,
                template=data.template,
                body=body,
                status=MessageStatus.PENDING
            )

            uow.emails.save(email_message)
            
        return email_message
