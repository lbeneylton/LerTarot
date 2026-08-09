"""Módulo para criação e decodificação de tokens JWT."""

from datetime import datetime, timedelta, timezone

from jose import JOSEError, jwt

# Configurações
from app.core.config import settings
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm


class JwtTokenService():

    def create_refresh_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=7)

        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": int(expire.timestamp()),
        }

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def create_access_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)

        payload = {
            "sub": str(user_id),
            "type": "access",
            "exp": int(expire.timestamp()),
        }

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def decode_token(self, token: str) -> dict[str, str] | None:
        """Verifica e decodifica um JWT. Retorna None se inválido ou expirado."""
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JOSEError:
            raise

    def get_user_id_from_token(self, token: str) -> int:
        payload = self.decode_token(token)

        if payload is None:
            raise ValueError("Token inválido ou expirado")

        return int(payload["sub"])
