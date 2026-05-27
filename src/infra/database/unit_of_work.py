from sqlalchemy.orm import Session
from contextlib import AbstractContextManager
from src.app.core.db import SessionLocal  # sua factory de session
from src.app.users.repository import UserRepository


class UnitOfWork:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.users = UserRepository(self.session)
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type:
                self.session.rollback()
            else:
                self.session.commit()
        finally:
            self.session.close()


class UnitOfWork(AbstractContextManager):
    def __init__(self):
        self.session: Session | None = None
        self.users: UserRepository | None = None

    def __enter__(self):
        self.session = SessionLocal()
        self.users = UserRepository(self.session)
        return self
