from collections.abc import Callable
from contextlib import AbstractContextManager

from sqlalchemy.orm import Session

from app.db import session as db_session
from app.users.repository import UserRepository


class UnitOfWork(AbstractContextManager["UnitOfWork"]):
    def __init__(
        self,
        session_factory: Callable[[], Session] | None = None,
    ) -> None:
        self._session_factory = session_factory or db_session.SessionLocal
        self.session: Session | None = None
        self.users: UserRepository | None = None

    def __enter__(self) -> "UnitOfWork":
        self.session = self._session_factory()
        self.users = UserRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session is None:
            return
        try:
            if exc_type:
                self.session.rollback()
            else:
                self.session.commit()
        finally:
            self.session.close()
