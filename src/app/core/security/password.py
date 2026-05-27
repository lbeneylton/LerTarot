"""Cria contexto da senha com algortimo de criptografia argon2
E com possibilidade futura de usar novos algoritmos futuros."""
from argon2 import PasswordHasher
from src.app.core.exceptions import PasswordError


# Criando o contexto da senha, o esquema de hash utilizado é o bcrypt
# E o deprecated="auto" indica que os hashes antigos serão atualizados automaticamente
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
