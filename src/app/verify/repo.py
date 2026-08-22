from datetime import datetime, timezone
from sqlalchemy import select, update
from app.db.contract import SessionContract
from app.verify.models import CodeEmail

class CodeEmailRepo:
    def __init__(self, session: SessionContract) -> None:
        self.session = session

    def save(self, verification: CodeEmail) -> CodeEmail:
        self.session.add(verification)
        return verification

    def invalidate_user_codes(self, user_id: int) -> None:
        now = datetime.now(timezone.utc)
        stmt = (
            update(CodeEmail)
            .where(
                CodeEmail.user_id == user_id,
                CodeEmail.used_at.is_(None)
            )
            .values(used_at=now)
        )
        self.session.execute(stmt)

    def get_latest_active(self, user_id: int) -> CodeEmail | None:
        now = datetime.now(timezone.utc)
        stmt = (
            select(CodeEmail)
            .where(
                CodeEmail.user_id == user_id,
                CodeEmail.used_at.is_(None),
                CodeEmail.expires_at > now
            )
            .order_by(CodeEmail.created_at.desc())
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def exist_this_code_active(self, user_id: int, code_hash: str) -> bool:
        # Verifica se o código específico existe e está ativo
        now = datetime.now(timezone.utc)
        stmt = (
            select(CodeEmail)
            .where(
                CodeEmail.user_id == user_id,
                CodeEmail.code_hash == code_hash,
                CodeEmail.used_at.is_(None),
                CodeEmail.expires_at > now
            )
        )
        result = self.session.execute(stmt).scalar_one_or_none()
        return result is not None