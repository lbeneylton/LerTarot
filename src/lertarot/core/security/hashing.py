"""Cria contexto da senha com algortimo de criptografia argon2
E com possibilidade futura de usar novos algoritmos futuros."""
from passlib.context import CryptContext
from .exceptions import SenhaGrandeError

# Criando o contexto da senha, o esquema de hash utilizado é o bcrypt
# E o deprecated="auto" indica que os hashes antigos serão atualizados automaticamente
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

# Tamaho máximo de caracteres por senha
MAX_SENHA_BYTES = 30


def gerar_hash(senha: str) -> str:
    """Função que gera o hash da senha
        tira espaços em branco e verifica se a senha tem até 30 bytes
    """
    senha = senha.strip()
    tamanho = len(senha.encode("utf-8"))

    if tamanho > MAX_SENHA_BYTES:
        raise SenhaGrandeError(
            f"Senha muito longa (máx {MAX_SENHA_BYTES} bytes)"
        )

    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Retorna verdadeiro se a senha e o hash corresponderem"""
    return pwd_context.verify(
        senha.strip(),
        senha_hash.strip()
    )
