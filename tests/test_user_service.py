import pytest

from app.core.exceptions import ConflictError
from app.domains.users.models import UserRole
from app.domains.users.schemas import UserCreate
from app.domains.users.use_cases.create_user import CreateUserService
from app.db.session import AsyncSessionLocal
from app.db.uow import SqlAlchemyUnitOfWork
from app.security.hasher import Argon2Hasher
from app.domains.verify.services import VerifyEmailService


@pytest.mark.anyio
async def test_create_user_persists() -> None:
    async with AsyncSessionLocal() as session:
        uow = SqlAlchemyUnitOfWork(session)
        hasher = Argon2Hasher()
        email_verificator = VerifyEmailService(uow, hasher)
        service = CreateUserService(uow, hasher, email_verificator)

        data = UserCreate(
            username="maria",
            email="maria@example.com",
            password="senha1234",
            role=UserRole.CLIENTE,
        )
        created = await service.create_user(data)

        assert created.user_id is not None
        assert created.email == "maria@example.com"
        assert created.username == "maria"


@pytest.mark.anyio
async def test_create_user_duplicate_email_raises_conflict() -> None:
    async with AsyncSessionLocal() as session:
        uow = SqlAlchemyUnitOfWork(session)
        hasher = Argon2Hasher()
        email_verificator = VerifyEmailService(uow, hasher)
        service = CreateUserService(uow, hasher, email_verificator)

        data = UserCreate(
            username="duplicada",
            email="duplicada@example.com",
            password="senha1234",
            role=UserRole.CLIENTE,
        )
        await service.create_user(data)

        with pytest.raises(ConflictError):
            await service.create_user(data)
