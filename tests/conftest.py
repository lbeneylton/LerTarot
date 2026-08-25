import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite://"
os.environ["DEV_DATABASE_URL"] = "sqlite+aiosqlite://"
os.environ["PROD_DATABASE_URL"] = "sqlite+aiosqlite://"

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

import app.db.registry  # noqa: F401
from app.db.base import Base
from app.db import session as session_module
from app.db.connection import get_session

test_async_engine = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

session_module.async_engine = test_async_engine
session_module.AsyncSessionLocal = TestAsyncSessionLocal

from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
async def db_schema():
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def async_client():
    async def _override_get_session():
        async with TestAsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_session] = _override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def user_payload():
    return {
        "username": "mariasilva",
        "email": "maria@example.com",
        "password": "senha1234",
        "role": "CLIENTE",
    }
