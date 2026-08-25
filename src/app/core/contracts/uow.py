from typing import Protocol, Any


class UnitOfWorkContract(Protocol):
    users: Any
    email_codes: Any
    emails: Any
    password_recovery: Any
    session: Any

    async def __aenter__(self) -> "UnitOfWorkContract": ...
    async def __aexit__(self, exc_type, exc_value, traceback) -> None: ...
