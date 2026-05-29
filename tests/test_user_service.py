import pytest

from app.core.exceptions import ConflictError
from app.users.enums import UserType
from app.users.models import Client, Reader, User
from app.users.schemas import UserCreate
from app.users.services import UserService, build_user


def test_build_user_client():
    data = UserCreate(
        name="Ana",
        email="ana@example.com",
        password="senha1234",
        user_type=UserType.client,
    )
    user = build_user(data)
    assert isinstance(user, Client)
    assert user.user_type == UserType.client


def test_build_user_reader():
    data = UserCreate(
        name="João",
        email="joao@example.com",
        password="senha1234",
        user_type=UserType.reader,
        bio="Tarólogo há 10 anos",
    )
    user = build_user(data)
    assert isinstance(user, Reader)
    assert user.bio == "Tarólogo há 10 anos"


def test_build_user_admin():
    data = UserCreate(
        name="Admin",
        email="admin@example.com",
        password="senha1234",
        user_type=UserType.admin,
    )
    user = build_user(data)
    assert type(user) is User
    assert user.user_type == UserType.admin


def test_create_user_persists(session_factory):
    service = UserService(session_factory=session_factory)
    data = UserCreate(
        name="Maria",
        email="maria@example.com",
        password="senha1234",
        user_type=UserType.client,
    )
    user = service.create_user(data)

    assert user.user_id is not None
    assert user.email == "maria@example.com"


def test_create_user_duplicate_email_raises_conflict(session_factory):
    service = UserService(session_factory=session_factory)
    data = UserCreate(
        name="Maria",
        email="duplicada@example.com",
        password="senha1234",
        user_type=UserType.client,
    )
    service.create_user(data)

    with pytest.raises(ConflictError):
        service.create_user(data)
