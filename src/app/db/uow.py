# Repositories

from app.users.repo import UserRepo
from app.verify.repo import CodeEmailRepo
from emails.repo import EmailMessageRepo

from app.db.contract import SessionContract


class SqlAlchemyUnitOfWork:
    def __init__(self, session: SessionContract):
        self.session = session

        # Adicionar futuros repos
        self.users = UserRepo(session)
        self.email_codes = CodeEmailRepo(session)
        self.emails = EmailMessageRepo(session)
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
      