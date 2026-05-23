from passlib.context import CryptContext

# Criando o contexto da senha, o esquema de hash utilizado é o bcrypt
# E o deprecated="auto" indica que os hashes antigos serão atualizados automaticamente
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


# Classe de erro de senha
class SenhaGrande(Exception):
    pass


def gerar_hash(senha: str) -> str:
    """Função que gera o hash da senha
        tira espaços em branco e verifica se a senha tem até 30 bytes
    """
    senha = senha.strip()
    tamanho = len(senha.encode("utf-8"))

    if tamanho > 30:
        raise SenhaGrande("Senha muito longa (máx 30 bytes)")

    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha.strip(), senha_hash.strip())