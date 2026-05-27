# Importação da Factory Session
from src.app.core.database.session import SessionLocal


def get_session():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
