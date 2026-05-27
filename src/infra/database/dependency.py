# Importação da Factory Session
from infra.database.session import SessionLocal


def get_session():
    """Função geradora de funções"""
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
