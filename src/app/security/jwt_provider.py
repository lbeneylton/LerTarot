"""Módulo para criação e decodificação de tokens JWT."""
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError, ExpiredSignatureError

# Configurações
from app.core.config import settings

from app.core.exceptions import UnauthorizedError

SECRET_KEY = settings.auth.secret_key
ALGORITHM = settings.auth.algorithm
REFRESH_EXPIRE_DAYS = settings.auth.refresh_expire_days
ACCESS_EXPIRE_MINUTES = settings.auth.access_expire_minutes


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
    
    def create_refresh_token(self, user_id: int, version:int) -> str:
        now = datetime.now(timezone.utc)

        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "token_version": str(version),
            "iat": now,
            "exp": now + timedelta(
                days=self.refresh_exp_d
            ),
        }

        return self._encode(payload)

    def create_access_token(self, user_id: int, version: int) -> str:
        now = datetime.now(timezone.utc)

        payload = {
            "sub": str(user_id),
            "type": "access",
            "token_version": str(version),        
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
            raise UnauthorizedError("Token expirado")
        except JWTError:
            raise UnauthorizedError("Assinatura inválida")

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



jwt_provider = JwtTokenService(
    secret_key=SECRET_KEY,
    algorithm=ALGORITHM,
    access_exp_m=ACCESS_EXPIRE_MINUTES,
    refresh_exp_d=REFRESH_EXPIRE_DAYS
)