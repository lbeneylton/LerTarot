import pytest

from app.core.exceptions import ConflictError
from app.modules.users.models import UserRole
from app.modules.users.schemas import UserCreate
from app.modules.auth.use_cases import CreateUserService
from app.modules.email_verification.services import VerifyEmailService
from app.db.session import AsyncSessionLocal
from app.db.uow import SqlAlchemyUnitOfWork
from app.security.hasher import Argon2Hasher


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
