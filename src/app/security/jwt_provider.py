"""Módulo para criação e decodificação de tokens JWT."""

from datetime import datetime, timedelta, timezone

from jose import JOSEError, JWTError, jwt

# Configurações
from app.core.config import settings


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm


class JwtTokenService:
    def create_refresh_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=7)

        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": int(expire.timestamp()),
        }

        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

    def create_access_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)

        payload = {
            "sub": str(user_id),
            "type": "access",
            "exp": int(expire.timestamp()),
        }

        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

    def _decode_token(self, token: str) -> dict:
        """
        Verifica assinatura e expiração do JWT.

        Lança JWTError caso o token seja inválido ou expirado.
        """
        try:
            return jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
            )
        except JOSEError:
            raise

    def decode_refresh_token(self, token: str) -> dict:
        """
        Valida e decodifica especificamente um refresh token.

        Verifica:
        - assinatura;
        - expiração;
        - existência do subject;
        - tipo do token.

        Lança JWTError caso o token seja inválido.
        """

        payload = self._decode_token(token)

        if payload.get("type") != "refresh":
            raise JWTError("Token não é um refresh token")

        if "sub" not in payload:
            raise JWTError("Refresh token sem usuário")

        return payload

    def decode_access_token(self, token: str) -> dict:
        """
        Valida e decodifica especificamente um access token.

        Verifica:
        - assinatura;
        - expiração;
        - existência do subject;
        - tipo do token.

        Lança JWTError caso o token seja inválido.
        """

        payload = self._decode_token(token)

        if payload.get("type") != "access":
            raise JWTError("Token não é um access token")

        if "sub" not in payload:
            raise JWTError("Refresh token sem usuário")

        return payload

    def get_user_id_from_token(self, token: str) -> int:
        """
        Retorna o ID do usuário presente no token.
        """

        payload = self._decode_token(token)

        if "sub" not in payload:
            raise JWTError("Token sem identificação do usuário")

        return int(payload["sub"])
