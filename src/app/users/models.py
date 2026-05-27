from datetime import datetime
from uuid import UUID, uuid7

from sqlalchemy import (
    String,
    Uuid,
    Index,
    DateTime,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from infra.database.base import Base
from src.app.users.enums import UserType


class User(Base):
    """
    Representa um usuário da aplicação.

    Attributes:
        user_id:
            Identificador único UUIDv7.

        nome:
            Nome completo do usuário.

        email:
            Email único utilizado para autenticação.

        senha_hash:
            Hash da senha do usuário.

        role:
            Papel/permissão do usuário no sistema (padrão "client").

        created_at:
            Data de criação do registro.

        deleted_at:
            Data de soft delete. NULL indica usuário ativo.
    """
    __tablename__ = "users"

    __table_args__ = (
        Index("idx_users_email_active", "email", unique=True),
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid7,
    )

    nome: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    senha_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    type: Mapped[UserType] = mapped_column(
        String(10),
        default=UserType.client
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
