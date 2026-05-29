"""Hash e verificação de senhas com Argon2."""
from argon2 import PasswordHasher

password_hasher = PasswordHasher()


# Cria hash da senha
def hash_password(password: str) -> str:
    return password_hasher.hash(password)

# verifica se a senha gera o hash


def verify_password(
    password: str,
    hashed_password: str
) -> bool:

    try:
        return password_hasher.verify(
            hashed_password,
            password
        )

    except Exception:
        return False
