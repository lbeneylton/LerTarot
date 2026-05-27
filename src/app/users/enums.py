from enum import Enum


class UserType(str, Enum):
    """
    Perfis de acesso disponíveis no sistema.

    Attributes:
        admin:
            Acesso total ao sistema.

        reader:
            Usuarios que podem cadastrar serviços, 

        client:
            Usuário final da plataforma.
    """
    admin = "admin"
    reader = "reader"
    client = "client"
