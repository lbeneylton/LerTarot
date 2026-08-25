from typing import Protocol, Any, Optional

class CacheContract(Protocol):
    """Contrato que define as operações básicas de cache.
    
    Independe da implementação (Redis, Memcached, ou Memória Local).
    """

    async def get(self, key: str) -> Optional[str]:
        """Recupera um valor do cache pelo seu identificador (key)."""
        ...

    async def set(self, key: str, value: str, expire_seconds: Optional[int] = None) -> None:
        """Salva um valor no cache com um tempo de expiração opcional."""
        ...

    async def delete(self, key: str) -> None:
        """Remove um valor do cache pelo seu identificador (key)."""
        ...
