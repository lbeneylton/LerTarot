from enum import Enum


class UserType(str, Enum):
    """
    Perfis de acesso disponíveis no sistema.

    Tipos:
    
        ADMIN:
            Acesso total ao sistema.

        READER:
            Usuarios que podem cadastrar serviços, 

        CLIENTE:
            Usuário final da plataforma.
    """
    ADMIN = "ADMIN"
    READER = "READER"
    CLIENTE = "CLIENTE"
