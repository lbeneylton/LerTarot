import os

os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.db.registry  # noqa: F401 — registra models no metadata
from app.db.base import Base
from app.db import session as session_module

# SQLite em memória exige StaticPool para compartilhar o mesmo banco entre conexões
session_module.engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
session_module.SessionLocal = sessionmaker(
    bind=session_module.engine,
    autocommit=False,
    autoflush=False,
)

from app.main import app  # noqa: E402 — após reconfigurar o engine de teste


@pytest.fixture(autouse=True)
def db_schema():
    Base.metadata.drop_all(session_module.engine)
    Base.metadata.create_all(session_module.engine)
    yield


@pytest.fixture
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture
def session_factory(engine):
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def user_payload():
    return {
        "name": "Maria Silva",
        "email": "maria@example.com",
        "password": "senha1234",
        "user_type": "client",
    }
