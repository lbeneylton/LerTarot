import logging
from app._sender.interface import EmailSender

logger = logging.getLogger("app.email_mock")

class MockEmailSender(EmailSender):
    def send(self, to: str, subject: str, body: str) -> None:
        logger.info(
            f"=== [MOCK EMAIL SENDER] ===\n"
            f"Para: {to}\n"
            f"Assunto: {subject}\n"
            f"Corpo:\n{body}\n"
            f"==========================="
        )
