from typing import Any, Protocol


class ScalarResultContract(Protocol):
    def all(self) -> list[Any]: ...
        
    def first(self) -> Any | None: ...


class QueryResultContract(Protocol):
    rowcount:int
    
    def scalars(self) -> Any:
        ...

    def scalar(self) -> Any:
        ...

    def scalar_one(self) -> Any:
        ...

    def scalar_one_or_none(self) -> Any:
        ...

    def all(self) -> list[Any]:
        ...

    def first(self) -> Any:
        ...
    
        
class StatementContract(Protocol):
    def where(self, *criteria: Any) -> "StatementContract": ...

    def values(self, **values: Any) -> "StatementContract": ...


class SessionContract(Protocol):
    def add(
        self,
        instance: object,
        *_args: Any,
        **_kwargs: Any,
    ) -> None:
        ...

    def execute(
        self,
        statement: Any,
        *_args: Any,
        **_kwargs: Any,
    ) -> QueryResultContract:
        ...

    def close(self) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...

    def flush(self) -> None:
        ...

    def refresh(
        self,
        instance: object,
    ) -> None:
        ...

    def __enter__(self) -> "SessionContract":
        ...

    def __exit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        ...
        
        
class SessionFactoryContract(Protocol):
    def __call__(self) -> SessionContract:
        ...
