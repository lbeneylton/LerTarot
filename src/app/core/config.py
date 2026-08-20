"""Configurações da aplicação."""

from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class CredentialsSettings(BaseModel):
    """Credenciais de acesso ao serviço de email."""
    username: str
    password: str


class EmailSettings(BaseModel):
    """Configurações de e-mail."""
    host: str
    port: str
    
    credentials: CredentialsSettings


class DatabaseSettings(BaseModel):
    """Configurações de conexão com o banco de dados."""

    url_dev: str
    url_prod: str

    @property
    def url(self) -> str:
        """Retorna a URL do banco conforme o ambiente."""
        if settings.env.upper() == "PROD":
            return f"postgresql+psycopg://{self.url_prod}"
        
        return f"postgresql+psycopg://{self.url_dev}"

class AuthSettings(BaseModel):
    """Configurações relacionadas à autenticação."""
    secret_key: str
    algorithm: str = "HS256"

    access_expire_minutes: int = 5
    refresh_expire_days: int = 30


class PaymentSettings(BaseModel):
    """Configurações do gateway de pagamento."""
    api_key: str 
    base_url: str 
    timeout: int = 30



class Settings(BaseSettings):
    """Configurações gerais da aplicação."""

    env: str = "DEV"

    database: DatabaseSettings 
    auth: AuthSettings 
    email: EmailSettings 
    payment: PaymentSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Retorna a instância única das configurações."""
    return Settings() # type: ignore[call-arg]


settings = get_settings()
