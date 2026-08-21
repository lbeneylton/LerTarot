"""Hash e verificação de senhas com Argon2."""
from argon2 import PasswordHasher


class Argon2Hasher():

    def __init__(self):
        self.hasher = PasswordHasher()

    # Cria hash da senha
    def hash(self, password: str) -> str:
        return self.hasher.hash(password)

    # verifica se a senha gera o hash

    def verify_hash(
        self,
        password: str,
        password_hash: str
    ) -> bool:

        try:
            return self.hasher.verify(
                password_hash,
                password
            )

        except Exception:
            return False


def get_hasher() -> Argon2Hasher:
    return Argon2Hasher()