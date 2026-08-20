# Importação da Factory Session
from app.db.session import SessionLocal


def get_session():
    """Função geradora de funções"""
    session = SessionLocal()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
