from enum import Enum
from datetime import datetime
from sqlalchemy import (
    Integer,
    Identity,
    String,
    DateTime,
    Enum as SQLEnum,
    func,
    JSON
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MessageStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SENT = "SENT"
    RETRY = "RETRY"
    FAILED = "FAILED"


class EmailMessage(Base):
    """
    idempotency_key\n
    to\n
    subject\n
    body (template)\n
    variables NULLABLE\n
    """
    
    __tablename__ = "email_messages"
    
    message_id: Mapped[int] = mapped_column(
        Integer,
        Identity(always=False),
        primary_key=True
    )
    
    idempotency_key: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True
    )
    
    to: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False
    )

    subject: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    body: Mapped[str] = mapped_column(
        nullable=False
    )
    
    variables = mapped_column(JSON, nullable=True)

    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    next_retry_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    status: Mapped[MessageStatus] = mapped_column(
        SQLEnum(
            MessageStatus,
            name="message_status"
        ),
        default=MessageStatus.PENDING,
        nullable=False,
        index=True
    )
    
      
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
    )
    
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    error: Mapped[str | None] = mapped_column(
        nullable=True
    )