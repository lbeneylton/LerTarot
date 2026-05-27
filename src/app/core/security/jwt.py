from jose import jwt, JWTError, ExpiredSignatureError, JOSEError

from datetime import datetime, timedelta, timezone
from src.app.core.config import settings

# Segurança e autentificação services
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm


# ---- Criação de Json Token Web a partir de um dict
def create_access_token(data: dict, expire_minutes=30) -> str:
    """Função que cria um token com um dicionario e um timedelta,
    timedelta padrão de 30 minutos"""
    payload = data.copy()

    # Cálculo do tempo de expirção do jwt
    expire = (
        datetime.now(timezone.utc) + timedelta(expire_minutes)
    )

    # Adicionado o tempo de expiração ao dict do jwt
    # e retorno do jwt codificado
    payload.update({
        "exp": int(expire.timestamp())
    })

    header = {"alg": ALGORITHM}

    return jwt.encode(
        header,
        payload,
        SECRET_KEY
    )


def decode_token(token: str) -> dict | None:
    """Verifica e decodifica um JWT.
    retorna None se der erro"""
    try:  # Tenta fazer o decode e retornar o payload
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JOSEError:
        return None
