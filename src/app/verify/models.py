
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.users.models import User

from datetime import datetime, timezone

from sqlalchemy import (
    Integer,
    Identity,
    String,
    ForeignKey,
    DateTime,
    func
)

from sqlalchemy.orm import(
    Mapped,
    mapped_column
)

from app.db.base import Base


class CodeEmail(Base):
    __tablename__ = "codes_email_verifications"
    
    code_id:  Mapped[int] = mapped_column(
        Integer,
        Identity(always=False),
        primary_key=True
    )
    
    user_id :Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )
    
    code_hash:Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    expires_at:Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
  
    used_at:Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    attempts: Mapped [int]= mapped_column(
        Integer,
        nullable=False,
        default=0 
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
    )
    
    
    @property
    def code_expirado(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at