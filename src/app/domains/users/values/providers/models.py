from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domains.users.models import User

# Tipos
from datetime import datetime

from app.db.base import Base

from sqlalchemy import (
    String,
    DateTime,
    Index,
    Integer,
    ForeignKey,
    Identity,
    UniqueConstraint,
    func
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)


class Provider(Base):
    """
    provider: str not null
    """

    __tablename__ = "providers"

    provider_id: Mapped[int] = mapped_column(
        Integer,
        Identity(always=False),
        primary_key=True
    )

    provider: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        unique=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )


class UserProvider(Base):
    """
    user_id OP\n
    provider_id FK\n
    user\n
    """
    __tablename__ = "user_providers"

    user_provider_id: Mapped[int] = mapped_column(
        Integer,
        Identity(always=False),
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    provider_id: Mapped[int] = mapped_column(
        ForeignKey(
            "providers.provider_id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    __table_args__ = (
        Index(
            "ix_providers_user_id_provider_active",
            user_id,
            provider_id,
            postgresql_where=deleted_at.is_(None),
        ),
        UniqueConstraint(
            "user_id",
            "provider_id",
            name="uq_user_provider"
        )

    )
