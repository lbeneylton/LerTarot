import logging
from providers.email_sender.get_sender import EmailSender

logger = logging.getLogger("app.email_mock")

class MockEmailSender(EmailSender):
    def send_text(
        self, to: 
        str, subject: str | None, 
        body: str | None,
        template: str | None,
        variables: str | None
        
        ) -> None:
        logger.info(
            f"=== [MOCK EMAIL SENDER] ===\n"
            f"Para: {to}\n"
            f"Assunto: {subject}\n"
            f"Corpo:\n{body}\n"
            f"Template:\n{template}\n"
            f"variables:\n{variables}\n"
            f"==========================="
        )
    def send_template(
        self, to: 
        str, subject: str | None, 
        body: str | None,
        template: str | None,
        variables: str | None
        
        ) -> None:
        logger.info(
            f"=== [MOCK EMAIL SENDER] ===\n"
            f"Para: {to}\n"
            f"Assunto: {subject}\n"
            f"Corpo:\n{body}\n"
            f"Template:\n{template}\n"
            f"variables:\n{variables}\n"
            f"==========================="
        )
