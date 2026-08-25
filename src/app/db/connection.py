from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Gerador de sessão assíncrona do banco de dados para o FastAPI.

    Disponibiliza e fecha a sessão. O controle transacional (commit/rollback)
    é de responsabilidade EXCLUSIVA do SqlAlchemyUnitOfWork (uow.py).
    """
    async with AsyncSessionLocal() as session:
        yield session
