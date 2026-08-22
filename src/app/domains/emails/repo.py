from datetime import datetime, timezone
from typing import Sequence
from sqlalchemy import select

from app.db.contract import SessionContract
from app.domains.emails.model import EmailMessage, MessageStatus


class EmailMessageRepo:
    def __init__(self, session: SessionContract) -> None:
        self.session = session

    def save(self, email_message: EmailMessage) -> EmailMessage:
        self.session.add(email_message)
        return email_message

    def get_by_id(self, message_id: int) -> EmailMessage | None:
        stmt = select(EmailMessage).where(EmailMessage.message_id == message_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_idempotency_key(self, key: str) -> EmailMessage | None:
        stmt = select(EmailMessage).where(EmailMessage.idempotency_key == key)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_pending_emails_for_processing(self, limit: int = 10) -> Sequence[EmailMessage]:
        """Busca e-mails que estão PENDING ou RETRY e já passaram da hora de re-tentativa.
        
        Aplica bloqueio de linha (FOR UPDATE SKIP LOCKED) para suportar
        concorrência de múltiplos workers sem que eles enviem o mesmo e-mail.
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
        return self.session.execute(stmt).scalars().all()
