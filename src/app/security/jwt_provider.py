"""Módulo para criação e decodificação de tokens JWT."""
from uuid import uuid7
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError, ExpiredSignatureError

# Configurações
from app.core.config import settings

from app.core.exceptions import UnauthorizedError

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

# TODO pegar de configurações do .env
REFRESH_EXPIRE_DAYS = 30
ACCESS_EXPIRE_MINUTES = 5


class JwtTokenService:
    def __init__(
        self, 
        secret_key:str, 
        algorithm: str, 
        access_exp_m: int,
        refresh_exp_d:int 
    ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        
        self.access_exp_m = access_exp_m
        self.refresh_exp_d = refresh_exp_d
    
    def _encode(self, payload: dict) -> str:
        return jwt.encode(
            payload,
            self.secret_key,
            self.algorithm
        )
    
    def create_refresh_token(self, user_id: int) -> str:
        now = datetime.now(timezone.utc)

        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "jti": str(uuid7()),
            "iat": now,
            "exp": now + timedelta(
                days=self.refresh_exp_d
            ),
        }

        return self._encode(payload)

    def create_access_token(self, user_id: int) -> str:
        now = datetime.now(timezone.utc)

        payload = {
            "sub": str(user_id),
            "type": "access",
            "iat": now,
            "exp": now + timedelta(
                minutes=self.access_exp_m    
            ),
        }

        return self._encode(payload)

    def _decode_token(self, token: str) -> dict:
        """
        Verifica assinatura e expiração do JWT e subject.

        Lança JWTError caso o token seja inválido ou expirado.
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            
            if "sub" not in payload:
                raise JWTError("Token sem usuário identificado")
            
            return payload
            
        except ExpiredSignatureError:
            raise UnauthorizedError("Refresh token expirado")
        except JWTError:
            raise UnauthorizedError("Refresh token inválido")

    def decode_refresh_token(self, refresh_token: str) -> dict:
        """
        Valida e decodifica especificamente um refresh token.

        Verifica:
        - assinatura (_decode_token);
        - expiração (_decode_token);
        - existência do subject (_decode_token);
        - tipo do token.

        Lança JWTError caso o token seja inválido.
        """
        payload = self._decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise JWTError("Token não é um refresh token")

        return payload

    def decode_access_token(self, access_token: str) -> dict:
        """
        Valida e decodifica especificamente um access token.

        Verifica:
        - assinatura (_decode_token);
        - expiração (_decode_token);
        - existência do subject (_decode_token);
        - tipo do token.

        Lança JWTError caso o token seja inválido.
        """
        payload = self._decode_token(access_token)

        if payload.get("type") != "access":
            raise JWTError("Token não é um access token")

        return payload


    # def _get_sub(self, token: str) -> int:
    #     """
    #     Retorna o ID do usuário presente no token.
    #     """
    #     payload = self._decode_token(token)

    #     if "sub" not in payload:
    #         raise JWTError("Token sem identificação do usuário")

    #     return int(payload["sub"])