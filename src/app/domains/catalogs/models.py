from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domains.users.models import User
    
from datetime import datetime

from sqlalchemy import (
    Integer,
    Identity,
    ForeignKey,
    String,
    DateTime,
    func,
    UniqueConstraint
)    

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)
    

from app.db.base import Base
    
    
class Catalog(Base):
    __tablename__ = "catalogs"
    
    catalog_id: Mapped[int] = mapped_column(
        Integer,
        Identity(always=False),
        primary_key=True
    )
    
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("readers.user_id"),
        primary_key=True,
        nullable=False,
        unique=True
    )
    
    slug: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True
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
    
    __table_args__ =(
        UniqueConstraint("user_id"),
        UniqueConstraint("slug")
    )