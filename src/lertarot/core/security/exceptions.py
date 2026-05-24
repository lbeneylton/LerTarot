class TokenInvalidoError(Exception):
    """Token inválido ou expirado."""
    pass


# Classe de erro de senha
class SenhaGrandeError(Exception):
    """Senha excede tamanho permitido."""
    pass
