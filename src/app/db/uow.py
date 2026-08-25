from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.users.repo import UserRepo
from app.domains.verify.repo import CodeEmailRepo
from app.domains.users.values.providers.repo import ProviderRepo
from app.domains.users.values.password_recovery.repo import PasswordRecoveryRepo
from app.domains.emails.repo import EmailMessageRepo


class SqlAlchemyUnitOfWork:
    """Unit of Work Assíncrono com suporte a async with context manager."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

        self.users = UserRepo(session)
        self.email_codes = CodeEmailRepo(session)
        self.emails = EmailMessageRepo(session)
        self.providers = ProviderRepo(session)
        self.password_recovery = PasswordRecoveryRepo(session)

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.close()

    # Suporte síncrono legado para retrocompatibilidade em testes/worker caso necessário
    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass