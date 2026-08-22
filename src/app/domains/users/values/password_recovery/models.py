"""Modelos de usuários."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domains.users.models import User

from datetime import datetime, timezone

from sqlalchemy import (
    Integer,
    Identity,
    String,
    DateTime,
    ForeignKey,
    Index,
    func,
)

from sqlalchemy.orm import (
    Mapped, 
    mapped_column
)

from app.db.base import Base



class PasswordRecovery(Base):
    """ PasswordRecovery
        ------------------
        recovery_id
        user_id
        token_hash
        expires_at
        used_at
        created_at
        is_active
        """
        
        
    __tablename__ = "password_recovery"
    
    recovery_id: Mapped[int] = mapped_column(
        Integer,
        Identity(always=False),
        primary_key=True
    )
   
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        nullable= False,
    )
   
    token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
   
    expires_at: Mapped[datetime]= mapped_column(
       DateTime(timezone=True),
       nullable=False
   )
    
    used_at: Mapped[datetime]= mapped_column(
       DateTime(timezone=True),
       nullable=True
   )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    
    __table_args__ = (
        Index(
            "uq_recovery_token_not_used",
            token_hash,
            unique=True,
            postgresql_where=used_at.is_(None)
        ),
    
    )
    
