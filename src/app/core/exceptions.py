"""Classe Base dos erros de dominio
Por padrão o status_code será 400
e code DOMAIN_ERROR, 
que pode ser alterado a partir das heranças de cada dominio"""

""" Arquivo com as principais exceções do app"""


# Classe base para erros no app
class AppException(Exception):
    status_code = 400
    code = "APP_ERROR"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(AppException):
    status_code = 404
    code = "NOT_FOUND"


class UnauthorizedError(AppException):
    status_code = 401
    code = "UNAUTHORIZED"


class ForbiddenError(AppException):
    status_code = 403
    code = "FORBIDDEN"


class ConflictError(AppException):
    status_code = 409
    code = "CONFLICT"


class PasswordError(AppException):
    pass
