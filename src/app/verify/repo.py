from app.db.contract import SessionContract

from app.verify.models import CodeEmailVerificator

class CodeEmailRepo:
    def __init__(self, session: SessionContract) -> None:
        self.session = session
        
        
    def save(self, verification: CodeEmailVerificator):
        pass

    def invalidate_user_codes(self, user_id):
        # self.db.query(CodeEmailVerificator).filter(
                #     CodeEmailVerificator.user_id == user.id,
                #     CodeEmailVerificator.used_at.is_(None),
                # ).update(
                #     {"used_at": now},
                #     synchronize_session=False,
                # )
        pass
    
    def get_latest_active(self, user_id) -> CodeEmailVerificator | None:
          # verification = (
                #     self.db.query(CodeEmailVerificator)
                #     .filter(
                #         CodeEmailVerificator.user_id == user.id,
                #         CodeEmailVerificator.code_hash == code_hash,
                #         CodeEmailVerificator.used_at.is_(None),
                #     )
                #     .order_by(
                #         CodeEmailVerificator.created_at.desc()
                #     )
                #     .first()
                # )
        
        
        pass
    
    def exist_code(self, user_id, code):
        pass