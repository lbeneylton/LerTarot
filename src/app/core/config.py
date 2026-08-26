"""Configurações da aplicação."""

from functools import lru_cache

from pydantic import BaseModel, Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

class CredentialsSettings(BaseModel):
    """Credenciais de acesso ao serviço de email."""
    username: str
    password: str


class EmailSettings(BaseModel):
    """Configurações de e-mail."""
    host: str
    port: str
    
    timeout: int
    
    credentials: CredentialsSettings


class DatabaseSettings(BaseModel):
    """Configurações de conexão com o banco de dados."""
    url: str


class AuthSettings(BaseModel):
    """Configurações relacionadas à autenticação."""
    secret_key: str
    algorithm: str = "HS256"

    access_expire_minutes: int = 60
    refresh_expire_days: int = 30


class PaymentSettings(BaseModel):
    """Configurações do gateway de pagamento."""
    api_key: str 
    base_url: str 
    timeout: int = 30



class DiscordWebhookSettings(BaseModel):
    """Configurações dos Webhooks do Discord."""
    url_error: str = Field(
        default="",
        validation_alias=AliasChoices("url_error", "DISCORD_WEBHOOK_URL", "DISCORD_WEBHOOK__URL_ERROR")
    )
    url_users: str = Field(
        default="",
        validation_alias=AliasChoices("url_users", "DISCORD_WEBHOOK_USERS", "DISCORD_WEBHOOK__URL_USERS")
    )
    url_emails: str = Field(
        default="",
        validation_alias=AliasChoices("url_emails", "DISCORD_WEBHOOK_EMAILS", "DISCORD_WEBHOOK__URL_EMAILS")
    )


class Settings(BaseSettings):
    """Configurações gerais da aplicação."""

    env: str = "DEV"
    url_recovery_password: str = "localhost:8000/recovery-password"
    
    internal_api_key: str 
    redis_url: str = "redis://localhost:6379/0"
    
    discord_webhook: DiscordWebhookSettings = DiscordWebhookSettings()

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
