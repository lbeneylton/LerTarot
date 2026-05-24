"""Classe Base dos erros de dominio
Por padrão o status_code será 400
e code DOMAIN_ERROR, 
que pode ser alterado a partir das heranças de cada dominio"""


class DomainError(Exception):

    code = "DOMAIN_ERROR"
    status_code = 400

    def __init__(self, message):
        self.message = message
        super().__init__(message)
