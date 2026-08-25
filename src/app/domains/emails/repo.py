from datetime import datetime, timezone, timedelta
from typing import Sequence, Any
from sqlalchemy import select, update

from app.domains.emails.models import EmailMessage, MessageStatus


class EmailMessageRepo:
    def __init__(self, session: Any) -> None:
        self.session = session

    async def save(self, email_message: EmailMessage) -> EmailMessage:
        self.session.add(email_message)
        return email_message

    async def get_by_id(self, message_id: int) -> EmailMessage | None:
        stmt = select(EmailMessage).where(EmailMessage.message_id == message_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(self, key: str) -> EmailMessage | None:
        stmt = select(EmailMessage).where(EmailMessage.idempotency_key == key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_emails_for_processing(self, limit: int = 10) -> Sequence[EmailMessage]:
        """Busca e-mails PENDING ou RETRY prontos para processamento.
        
        Aplica bloqueio de linha (FOR UPDATE SKIP LOCKED) para concorrência de workers.
        """
        now = datetime.now(timezone.utc)
        stmt = (
            select(EmailMessage)
            .where(
                EmailMessage.status.in_([MessageStatus.PENDING, MessageStatus.RETRY]),
                (EmailMessage.next_retry_at.is_(None)) | (EmailMessage.next_retry_at <= now)
            )
            .order_by(EmailMessage.created_at.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def recover_stuck_processing_emails(self, timeout_seconds: int) -> int:
        now = datetime.now(timezone.utc)
        processing_limit = now - timedelta(seconds=timeout_seconds)

        stmt = (
            update(EmailMessage)
            .where(
                EmailMessage.status == MessageStatus.PROCESSING,
                EmailMessage.processing_started_at.is_not(None),
                EmailMessage.processing_started_at < processing_limit,
            )
            .values(
                status=MessageStatus.RETRY,
                next_retry_at=now,
                processing_started_at=None,
                error="PROCESSING timeout. Mensagem recuperada automaticamente.",
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0
