from abc import ABC, abstractmethod
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings
from app.core.logger import AppLogger

logger = AppLogger("EmailSender")

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


class EmailSender(ABC):
    @abstractmethod
    def send_text(self, to: str, subject: str, body: str) -> None:
        pass

    @abstractmethod
    def send_template(self, to: str, subject: str, template_name: str, variables: dict) -> None:
        pass


class MockEmailSender(EmailSender):
    def send_text(self, to: str, subject: str, body: str) -> None:
        logger.info(f"[MOCK EMAIL] Para: {to} | Assunto: {subject} | Corpo: {body[:50]}...")

    def send_template(self, to: str, subject: str, template_name: str, variables: dict) -> None:
        logger.info(f"[MOCK EMAIL TEMPLATE] Para: {to} | Assunto: {subject} | Template: {template_name} | Var: {variables}")


class SMTPEmailSender(EmailSender):
    def __init__(self) -> None:
        self.host = settings.email.host
        self.port = int(settings.email.port)
        self.username = settings.email.credentials.username
        self.password = settings.email.credentials.password
        self.timeout = int(settings.email.timeout)

        self.jinja_env = Environment(
            loader=FileSystemLoader(TEMPLATES_DIR),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def _validate(self, to: str, subject: str):
        if not to:
            raise ValueError("Destinatário (to) não pode ser nulo.")
        if not subject:
            raise ValueError("Assunto (subject) não pode ser nulo.")

    def _send_mime_message(self, to: str, subject: str, mime_msg: MIMEMultipart):
        if self.port == 465:
            server = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout)
        else:
            server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
            server.starttls()

        try:
            if self.username and self.password:
                server.login(self.username, self.password)
            server.sendmail(self.username or "noreply@lertarot.com", to, mime_msg.as_string())
            logger.info(f"E-mail enviado com sucesso para {to}.")
        finally:
            server.quit()

    def send_text(self, to: str, subject: str, body: str) -> None:
        self._validate(to, subject)
        msg = MIMEMultipart()
        msg["From"] = self.username or "noreply@lertarot.com"
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body or "", "plain", "utf-8"))
        self._send_mime_message(to, subject, msg)

    def send_template(self, to: str, subject: str, template_name: str, variables: dict) -> None:
        self._validate(to, subject)
        if not template_name.endswith(".html"):
            template_name += ".html"

        template_obj = self.jinja_env.get_template(template_name)
        rendered_body = template_obj.render(**(variables or {}))

        msg = MIMEMultipart()
        msg["From"] = self.username or "noreply@lertarot.com"
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(rendered_body, "html", "utf-8"))
        self._send_mime_message(to, subject, msg)


def get_sender() -> EmailSender:
    if settings.email.host and settings.email.credentials.username:
        return SMTPEmailSender()
    return MockEmailSender()
