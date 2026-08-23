from abc import ABC, abstractmethod

class EmailSender(ABC):
    @abstractmethod
    def send_text(self, to: str, subject: str, body: str) -> None:
        """Envia um e-mail.
        
        Args:
            to: E-mail do destinatário.
            subject: Assunto do e-mail.
            body: Conteúdo do e-mail (HTML ou texto simples).
        """
        pass
    
    @abstractmethod
    def send_template(self, to: str, subject: str, template: str, variable: dict) -> None:
        pass
