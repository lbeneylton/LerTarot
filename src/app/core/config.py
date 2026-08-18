"""Configurações da aplicação."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação."""
    database_url: str = "postgresql+psycopg://lucas@localhost:5432/ler_tarot"
    
    secret_key: str = "secret_key"
    algorithm: str = "HS256"
    
    refresh_expire_days: int = 30
    access_expire_minutes: int = 5
    
    env: str = "DEV"
    asaas_api_key: str = ""
    

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
