"""Transforma a pasta core em um módulo
e facilita a importação dessas classes, metodos e instancias:"""

# Instância do objeto de configuração do JWT
from .settings.security import security_settings

# Instância do objeto de configuração do banco
from .settings.database import database_settings

# Instância
from .logger.logger import logger as lg

# Função geradora de sessões com gerenciador de contexto
from .database.session import get_session

# Classe de error de domain basico
from .exception import DomainError

# Classe para metadados dos models
from .database.base import Base
