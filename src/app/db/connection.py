# Importação da Factory Session
from app.db.session import SessionLocal


def get_session():
    """Função geradora de funções"""
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
