from sqlalchemy.orm import Session

from app.emails.models import EmailVerificationCode

class EmailVerificationRepo:
    def __init__(self, session: Session) -> None:
        self.session = session
        
        
    def save(self, verification: EmailVerificationCode):
        pass

    def invalidate_user_codes(self, user_id):
        # self.db.query(EmailVerificationCode).filter(
                #     EmailVerificationCode.user_id == user.id,
                #     EmailVerificationCode.used_at.is_(None),
                # ).update(
                #     {"used_at": now},
                #     synchronize_session=False,
                # )
        pass
    
    def get_latest_active(self, user_id):
          # verification = (
                #     self.db.query(EmailVerificationCode)
                #     .filter(
                #         EmailVerificationCode.user_id == user.id,
                #         EmailVerificationCode.code_hash == code_hash,
                #         EmailVerificationCode.used_at.is_(None),
                #     )
                #     .order_by(
                #         EmailVerificationCode.created_at.desc()
                #     )
                #     .first()
                # )
        
        
        pass
    
    def exist_code(self, user_id, code):
        pass