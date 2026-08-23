import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from providers.email_sender.get_sender import EmailSender
from app.core.config import settings

logger = logging.getLogger("app.email_smtp")


class SMTPEmailSender(EmailSender):
    def __init__(self) -> None:
        self.host = settings.email.host
        self.port = int(settings.email.port) if settings.email.port else 587
        self.username = settings.email.credentials.username
        self.password = settings.email.credentials.password
        self.timeout = int(settings.email.timeout) if settings.email.timeout else 10

    def send(self, to: str, subject: str, body: str) -> None:
        message = MIMEMultipart()
        message["From"] = self.username
        message["To"] = to
        message["Subject"] = subject

        # Determina o tipo de conteúdo (HTML ou texto simples)
        content_type = "html" if ("<html>" in body or "<div" in body or "<p>" in body) else "plain"
        message.attach(MIMEText(body, content_type, "utf-8"))

        try:
            # Seleciona conexão SSL ou TLS baseada na porta
            if self.port == 465:
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout)
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
                server.starttls()
                
            try:
                if self.username and self.password:
                    server.login(self.username, self.password)
                
                server.sendmail(self.username, to, message.as_string())
                logger.info(f"E-mail enviado com sucesso para {to} usando SMTP")
            finally:
                server.quit()
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail via SMTP para {to}: {str(e)}")
            raise e
