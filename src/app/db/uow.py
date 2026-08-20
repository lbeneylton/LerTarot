# Repositories

from app.users.repo import UserRepo
from app.verify.repo import CodeEmailRepo

from app.db.contract import SessionContract


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: SessionContract):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()

        # Adicionar futuros repos
        self.users = UserRepo(self.session)
        self.email_codes = CodeEmailRepo(self.session)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type:
                self.session.rollback()
            else:
                self.session.commit()
        finally:
            self.session.close()