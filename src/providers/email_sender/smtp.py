from jinja2 import Template 
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from providers.email_sender.get_sender import EmailSender
from app.core.config import settings

from app.core.logger import AppLogger

logger = AppLogger("SMTP Email Sender")


class SMTPEmailSender(EmailSender):
    def __init__(self) -> None:
        self.host = settings.email.host
        self.port = int(settings.email.port)
        self.username = settings.email.credentials.username
        self.password = settings.email.credentials.password
        self.timeout = int(settings.email.timeout)

    def send(self, to: str, subject: str, body :str ) -> None:
        try:
            # =========================================================
            # DEBUG: mostra exatamente o que está chegando
            # =========================================================
            logger.info("========== INICIANDO ENVIO SMTP ==========")
            logger.info(f"to={to}")
            logger.info(f"subject={subject}")
            logger.info(f"body={body}")
            logger.info(f"body_type={type(body).__name__}")
            logger.info(f"host={self.host}")
            logger.info(f"port={self.port}")
            logger.info(f"username={self.username}")
            logger.info(f"password_configurada={bool(self.password)}")

            # Validações explícitas
            if body is None:
                raise ValueError(
                    "O body do e-mail está None. "
                    "O problema está antes do SMTPEmailSender."
                )

            if to is None:
                raise ValueError(
                    "O destinatário (to) está None."
                )

            if subject is None:
                raise ValueError(
                    "O subject está None."
                )

            # =========================================================
            # Monta mensagem
            # =========================================================
            message = MIMEMultipart()

            message["From"] = self.username
            message["To"] = to
            message["Subject"] = subject

            content_type = (
                "html"
                if (
                    "<html>" in body
                    or "<div" in body
                    or "<p>" in body
                )
                else "plain"
            )

            logger.info(f"content_type={content_type}")

            message.attach(
                MIMEText(
                    body,
                    content_type,
                    "utf-8",
                )
            )

            # =========================================================
            # Conexão SMTP
            # =========================================================
            logger.info(f"Conectando no SMTP {self.host}:{self.port}...")

            if self.port == 465:
                server = smtplib.SMTP_SSL(
                    self.host,
                    self.port,
                    timeout=self.timeout,
                )
            else:
                server = smtplib.SMTP(
                    self.host,
                    self.port,
                    timeout=self.timeout,
                )

                logger.info("Iniciando STARTTLS...")
                server.starttls()

            try:
                logger.info("Conexão SMTP estabelecida.")

                if self.username and self.password:
                    logger.info(f"Tentando autenticar como {self.username}...") 

                    server.login(
                        self.username,
                        self.password,
                    )

                    logger.info("Autenticação SMTP realizada.")

                logger.info(
                    f"Enviando e-mail para {to}..."
                )

                server.sendmail(
                    self.username,
                    to,
                    message.as_string(),
                )

                logger.info(
                    f"E-mail enviado com sucesso para {to}.",
                )

            finally:
                logger.info("Fechando conexão SMTP...")
                server.quit()

        except Exception:
            logger.exception(
                f"ERRO NO SMTPEmailSender | to={to} | subject={subject}",
                
            )

            # Repassa a exceção para o EmailWorker
            raise


    def send_template(self, to: str, subject: str, template: str, variable: dict) -> None:
        try:
            rendered_body = Template(template).render(**variable)

            self.send(
                to=to,
                subject=subject,
                body=rendered_body,
            )

        except Exception:
            logger.exception(
                f"ERRO AO RENDERIZAR/ENVIAR TEMPLATE | to={to} | subject={subject}"
            )
            raise