"""Configurações da aplicação."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação."""
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/lertarot"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    asaas_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
