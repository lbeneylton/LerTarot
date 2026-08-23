# Repositories

from app.domains.users.repo import UserRepo
from app.domains.verify.repo import CodeEmailRepo
from app.domains.users.values.providers.repo import ProviderRepo
from app.domains.users.values.password_recovery.repo import PasswordRecoveryRepo

from app.db.contract import SessionContract
from app.domains.emails.repo import EmailMessageRepo


class SqlAlchemyUnitOfWork:
    def __init__(self, session: SessionContract):
        self.session = session

        # Adicionar futuros repos
        self.users = UserRepo(session)
        self.email_codes = CodeEmailRepo(session)
        self.emails = EmailMessageRepo(session)
        
        self.providers = ProviderRepo(session)
        self.password_recovery = PasswordRecoveryRepo(session)
        
    def __enter__(self)  -> "SqlAlchemyUnitOfWork":
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
      