from datetime import datetime
from uuid import UUID, uuid7
from enum import Enum

from sqlalchemy import (
    ForeignKey,
    String,
    Uuid,
    Index,
    DateTime,
    func,
    Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.database.base import Base
from src.app.users.enums import UserType


class User(Base):
    """
    Representa um usuário da aplicação.

    Attributes:
        user_id:
            Identificador único UUIDv7.

        name:
            Nome completo do usuário.

        email:
            Email único utilizado para autenticação.

        password_hash:
            Hash da senha do usuário.

        user_type:
            Papel/permissão do usuário no sistema (padrão "client").

        created_at:
            Data de criação do registro.

        deleted_at:
            Data de soft delete. NULL indica usuário ativo.
    """
    __tablename__ = "users"

    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid7,
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    user_type: Mapped[UserType] = mapped_column(
        SAEnum(UserType, native_enum=False),
        nullable=False,
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

    __mapper_args__ = {
        "polymorphic_on": user_type,
        "polymorphic_identity": "user",
    }


# Índice único para email apenas de usuários ativos
Index(
    "idx_users_email_active",
    User.email,
    unique=True,
    postgresql_where=User.deleted_at.is_(None)
)


class Client(User):
    __tablename__ = 'clients'

    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.user_id"),
        primary_key=True
    )

    __mapper_args__ = {
        "polymorphic_identity": "client",
    }


class Reader(User):
    __tablename__ = 'readers'

    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.user_id"),
        primary_key=True
    )

    foto_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    bio: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    __mapper_args__ = {
        "polymorphic_identity": "reader",
    }
