"""Gerador de sessions"""
# Funções para gerar engine e sessões
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importação do objeto de configuração do banco
from src.app.core.config import settings

URL_DATABASE = settings.database_url

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
