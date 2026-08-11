"""Modelos de usuários."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.providers.models import UserProvider


from enum import Enum
from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    Index,
    String,
    Integer,
    DateTime,
    func,
    Enum as SQLEnum,
    Identity
)
from sqlalchemy.orm import Mapped, mapped_column
from app.users.enums import UserType
from app.db.base import Base


# -----------------------------------
# ROLES
# -----------------------------------
class UserRole(str, Enum):
    ADMIN = "ADMIN"
    READER = "READER"
    CLIENTE = "CLIENTE"


class User(Base):
    """
    Representa um usuário da aplicação.

    Attributes:
        user_id:
            Identificador único UUIDv7.

        username:
            Nome completo do usuário.

        email:
            Email único utilizado para autenticação.

        hash_password:
            Hash da senha do usuário.

        role:
            Papel/permissão do usuário no sistema (padrão "client").

        created_at:
            Data de criação do registro.

        deleted_at:
            Data de soft delete. NULL indica usuário ativo.
    """
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        Integer,
        Identity(always=False),
        primary_key=True
    )

    username: Mapped[str] = mapped_column(
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

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(
            UserRole,
            name="user_role"
        ),
        default=UserRole.CLIENTE,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __mapper_args__ = {
        "polymorphic_on": role,
        "polymorphic_identity": UserType.ADMIN,
    }

    __table_args__ = (
        Index(
            "ix_users_email_active",
            email,
            postgresql_where=deleted_at.is_(None),
        ),
        Index(
            "ix_users_username_active",
            username,
            postgresql_where=deleted_at.is_(None),
        ),
    )


class Client(User):
    """Representa um cliente da aplicação."""
    __tablename__ = 'clients'

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        primary_key=True
    )

    __mapper_args__ = {
        "polymorphic_identity": UserType.CLIENTE,
    }


class Reader(User):
    """Representa um leitor da aplicação."""
    __tablename__ = 'readers'

    user_id: Mapped[int] = mapped_column(
        Integer,
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
        "polymorphic_identity": UserType.READER,
    }
