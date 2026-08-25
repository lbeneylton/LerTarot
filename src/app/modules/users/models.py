from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import (
    Integer,
    Identity,
    String,
    Boolean,
    DateTime,
    Enum as SQLEnum,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserRole(str, Enum):
    CLIENTE = "CLIENTE"
    READER = "READER"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        Integer,
        Identity(always=False),
        primary_key=True
    )
    
    username: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
        nullable=False
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role"),
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    token_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    __mapper_args__ = {
        "polymorphic_on": role,
        "polymorphic_identity": UserRole.ADMIN,
    }


class Client(User):
    __mapper_args__ = {
        "polymorphic_identity": UserRole.CLIENTE,
    }


class Reader(User):
    __mapper_args__ = {
        "polymorphic_identity": UserRole.READER,
    }
