
from enum import Enum
from datetime import datetime


from sqlalchemy import (
    Integer,
    Identity,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    func,
    Enum as SQLEnum
)

from sqlalchemy.orm import (
    Mapped, 
    mapped_column
)

# Base
from app.db.base import Base


# Estados
class MessageStatus(str, Enum):
    PENDING = 1
    PROCESSING = 2
    SENT = 3
    RETRY = 4
    FAILED = 5


class EmailMensages(Base):
    __tablename__ = "email_messages"
    
    message_id: Mapped[int] = mapped_column(
        Integer,
        Identity(always=False),
        primary_key=True
    )
    
    to: Mapped[str]= mapped_column(
        index=True
    )

    subject: Mapped[str]= mapped_column(
        
    )

    template: Mapped[str]= mapped_column(
        index=True
    )

    body : Mapped[] = mapped_column(
        
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )
    
    
    next_retry_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    status: Mapped[MessageStatus]= mapped_column(
        SQLEnum(
            MessageStatus,
            name="user_role"
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
    
    send_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    error: Mapped[str] = mapped_column(
        
    )


    __mapper_args__ = {
        "polymorphic_on": status        
    }
    
    