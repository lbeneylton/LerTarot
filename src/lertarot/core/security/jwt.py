from jose import jwt, JWTError, ExpiredSignatureError

from datetime import datetime, timedelta, timezone
from lertarot.core import security_settings

from .exceptions import TokenInvalidoError

# Segurança e autentificação services
SECRET_KEY = security_settings.secret_key
ALGORITHM = security_settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = (
    security_settings.access_token_expire_minutes
)

# ---- Criação de Json Token Web a partir de um dict


def criar_token(
    data: dict,
    expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
) -> str:
    """Função que cria um token com um dicionario e um timedelta,
    timedelta padrão de 30 minutos"""
    to_encode = data.copy()

    # Cálculo do tempo de expirção do jwt
    expire = (
        datetime.now(timezone.utc) + expires_delta
    )

    # Adicionado o tempo de expiração ao dict do jwt
    # e retorno do jwt codificado
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verificar_token(token: str) -> dict:
    """Verifica e decodifica um JWT.
    Levanta erros se otoken tiver expirado ou for invalido"""
    try:  # Tenta fazer o decode e retornar o payload
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        sub = payload.get("sub")

        if sub is None:  # Garante que sempre terá um subject (role)
            raise TokenInvalidoError("Token sem subject")

        return payload

    except ExpiredSignatureError:
        raise TokenInvalidoError(
            "Token expirado"
        )

    except JWTError:
        raise TokenInvalidoError(
            "Token inválido"
        )
