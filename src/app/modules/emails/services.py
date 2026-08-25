import logging
from app.db.uow import SqlAlchemyUnitOfWork
from app.modules.emails.models import EmailMessage, MessageStatus
from app.modules.emails.schemas import MessageRequest

logger = logging.getLogger("emails.service")


class EmailService:
    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        self.uow = uow

    async def enqueue_email(
        self, 
        data: MessageRequest, 
        idempotency_key: str | None = None
    ) -> EmailMessage:
        template_or_body = data.template or data.body
        if not template_or_body:
            raise ValueError("É necessário fornecer o corpo ('body') ou um 'template' válido.")

        async with self.uow as uow:
            if idempotency_key:
                existing = await uow.emails.get_by_idempotency_key(idempotency_key)
                if existing:
                    logger.info(f"Requisição de e-mail duplicada interceptada. Chave: {idempotency_key}")
                    return existing

            email_message = EmailMessage(
                idempotency_key=idempotency_key,
                to=data.to,
                subject=data.subject,
                template=data.template,
                body=template_or_body,
                variables=data.variables or {},
                status=MessageStatus.PENDING,
            )

            await uow.emails.save(email_message)
            return email_message
