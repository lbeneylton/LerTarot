from jose import jwt, JWTError, ExpiredSignatureError

from datetime import datetime, timedelta, timezone
from core.config_sc import SC_settings

# Segurança e autentificação services
SECRET_KEY = SC_settings.config_security["Secret Key"]
ALGORITHM = SC_settings.config_security["Algorithm"]
ACCESS_TOKEN_EXPIRE_MINUTES = SC_settings.config_security["Token Minutes"]


class TokenInvalido(Exception):
    pass
# ---- Segurança e verificação de senhas com validação de tamanho ---- #


# ---- Criação de Json Token Web a partir de um dict
def criar_token(data: dict, time: timedelta = timedelta(minutes=30)) -> str:
    to_encode = data.copy()
    expire = (
        datetime.now(timezone.utc) + time
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(token: str) -> dict:
    """Verifica se o token ainda é valido"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except JWTError as e:
        raise TokenInvalido("Token inválido ou expirado", e)


def verificar_token_new(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except ExpiredSignatureError:
        # Token expirou
        raise TokenInvalido("Token expirado")
    except JWTError:
        # Qualquer outro erro (assinatura inválida)
        raise TokenInvalido("Token inválido")