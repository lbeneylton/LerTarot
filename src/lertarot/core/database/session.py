"""Gerador de sessions"""
# Funções para gerar engine e sessões
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importação do objeto de configuração do banco
from lertarot.core import database_settings

URL_DATABASE = database_settings.url_database

engine = create_engine(URL_DATABASE)

SessionLocal=sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        
        
# Teste de importação da url do banco        
def criar_sessao():
    return database_settings.url_database


if __name__ == "__main__":
    # Teste rápido do módulo
    print("URL do banco:", criar_sessao())

