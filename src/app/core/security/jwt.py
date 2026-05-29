"""Módulo para criação e decodificação de tokens JWT."""

from datetime import datetime, timedelta, timezone

from jose import JOSEError, jwt

from app.core.config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm


def create_access_token(data: dict, expire_minutes: int = 30) -> str:
    """Cria um JWT com expiração padrão de 30 minutos."""
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload["exp"] = int(expire.timestamp())

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    """Verifica e decodifica um JWT. Retorna None se inválido ou expirado."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JOSEError:
        return None
