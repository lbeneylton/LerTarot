from app.sender.interface import EmailSender
from app.sender.mock import MockEmailSender
from app.sender.smtp import SMTPEmailSender
from app.core.config import settings

def get_sender() -> EmailSender:
    """Retorna o provedor de e-mail adequado para o ambiente atual.
    
    Usa SMTPEmailSender apenas se as configurações de host e username estiverem preenchidas.
    Caso contrário, retorna MockEmailSender por segurança para evitar quebras de inicialização.
    """
    if settings.email.host and settings.email.credentials.username:
        return SMTPEmailSender()
    return MockEmailSender()