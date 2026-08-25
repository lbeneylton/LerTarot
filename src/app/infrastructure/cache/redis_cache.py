import redis.asyncio as redis
from typing import Optional

from app.core.config import settings
from app.core.contracts.cache import CacheContract

class RedisCache(CacheContract):
    """Implementação concreta de CacheContract usando Redis."""

    def __init__(self) -> None:
        # A conexão real será gerenciada pelo pool do redis
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)

    async def get(self, key: str) -> Optional[str]:
        return await self.redis_client.get(key)

    async def set(self, key: str, value: str, expire_seconds: Optional[int] = None) -> None:
        await self.redis_client.set(name=key, value=value, ex=expire_seconds)

    async def delete(self, key: str) -> None:
        await self.redis_client.delete(key)
