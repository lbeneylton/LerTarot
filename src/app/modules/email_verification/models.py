from datetime import datetime, timezone
from sqlalchemy import (
    Integer,
    Identity,
    String,
    DateTime,
    ForeignKey,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CodeEmail(Base):
    __tablename__ = "email_verification_codes"

    verification_id: Mapped[int] = mapped_column(
        Integer,
        Identity(always=False),
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        index=True,
        nullable=False,
    )

    code_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
