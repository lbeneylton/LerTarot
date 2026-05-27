from src.app.users.models import User

from datetime import datetime, UTC

from sqlalchemy.orm import Session
from sqlalchemy import select, Select

# from src.app.core.logger import logging
# logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _active_only(self) -> Select:
        return select(User).where(User.deleted_at.is_(None))

    def create(self, user: User) -> User:
        self.session.add(user)
        return user

    def get_active_by_id(self, user_id: int) -> User | None:
        return self.session.execute(
            self._active_only().where(User.user_id == user_id)
        ).scalar_one_or_none()

    def get_active_by_email(self, email: str) -> User | None:
        return self.session.execute(
            self._active_only().where(User.email == email)
        ).scalar_one_or_none()

    def update(self, user: User):
        self.session.add(user)
        return user

    def delete(self, user_id: int):  # sem commit
        user = self.get_active_by_id(user_id)

        if not user:
            return None

        user.deleted_at = datetime.now(UTC)
        self.session.add(user)
        return user
