"""Base para models do projeto
para usar na criação das tabelas por meio do alembic"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
