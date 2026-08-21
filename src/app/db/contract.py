from typing import Any, Protocol


class ScalarResultContract(Protocol):
    def all(self) -> list[Any]:
        ...


class QueryResultContract(Protocol):
    def scalars(self) -> ScalarResultContract:
        ...

    def scalar_one_or_none(self) -> Any | None:
        ...


class SessionContract(Protocol):
    def __call__(self) -> "SessionContract":
        ...

    def add(self, *args: Any, **kwargs: Any) -> None:
        ...

    def execute(self, *args: Any, **kwargs: Any) -> QueryResultContract:
        ...

    def close(self) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
        
    def flush(self) -> None:
        ...
        
    def refresh(self) -> object: ...