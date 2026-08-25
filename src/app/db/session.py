"""Gerador de sessions assíncronas do SQLAlchemy."""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

URL_DATABASE = settings.database.url

# Async Engine e AsyncSession
async_engine = create_async_engine(
    URL_DATABASE,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Engine Síncrona (para migrações Alembic ou scripts utilitários)
engine = create_engine(
    URL_DATABASE,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
