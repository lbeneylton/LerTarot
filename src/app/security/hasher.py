"""Hash e verificação de senhas com Argon2."""
from argon2 import PasswordHasher


class Argon2Hasher():

    def __init__(self):
        self.password_hasher = PasswordHasher()

    # Cria hash da senha
    def hash_password(self, password: str) -> str:
        return self.password_hasher.hash(password)

    # verifica se a senha gera o hash

    def verify_password(
        self,
        password: str,
        password_hash: str
    ) -> bool:

        try:
            return self.password_hasher.verify(
                password_hash,
                password
            )

        except Exception:
            return False
