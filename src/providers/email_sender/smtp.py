from jinja2 import Template, Environment, FileSystemLoader, select_autoescape
from pathlib import Path
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
        
        templates_dir = Path(__file__).resolve().parent / "templates"

        self.jinja_env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )     
        
    def _validate_text(self, to: str, subject: str, body: str):
        # Validações explícitas
        if body is None:
            raise ValueError(
                "O body/template do e-mail está None. "
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
            


    def send_text(self, to: str, subject: str, body :str ) -> None:
        try:
            # =========================================================
            # DEBUG: mostra exatamente o que está chegando
            # =========================================================
            logger.debug("========== INICIANDO ENVIO SMTP ==========")
            logger.debug(f"to={to}")
            logger.debug(f"subject={subject}")
            logger.debug(f"body={body}")
            logger.debug(f"body_type={type(body).__name__}")
            logger.debug(f"host={self.host}")
            logger.debug(f"port={self.port}")
            logger.debug(f"username={self.username}")
            logger.debug(f"password_configurada={bool(self.password)}")

            self._validate_text(to, subject, body)

            # =========================================================
            # Monta mensagem
            # =========================================================
            message = MIMEMultipart()

            message["From"] = self.username
            message["To"] = to
            message["Subject"] = subject

            message.attach(
                MIMEText(
                    body,
                    "plain",
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


    def send_template(
        self,
        to: str,
        subject: str,
        template: str,
        variable: dict | None = None,
    ) -> None:
        try:
            logger.debug("========== RENDERIZANDO TEMPLATE ==========")
            logger.debug(f"to={to}")
            logger.debug(f"subject={subject}")
            logger.debug(f"template_type={type(template).__name__}")
            logger.debug(f"template={template}")
            logger.debug(f"variable={variable}")
            logger.debug(f"variable_type={type(variable).__name__}")

            self._validate_text(to, subject, template)

            if variable is None:
                variable = {}

            if not isinstance(variable, dict):
                raise TypeError(
                    f"variable precisa ser dict, mas recebeu {type(variable).__name__}"
                )
                
            if variable is None:
                raise ValueError(
                    "As variáveis do template não foram fornecidas."
                )

            logger.debug("Iniciando renderização Jinja2...")

            template_obj = self.jinja_env.get_template(template)
            rendered_body = template_obj.render(**variable)


            logger.debug("Template renderizado com sucesso.")
            logger.debug(f"rendered_body_type={type(rendered_body).__name__}")
            logger.debug(f"rendered_body={rendered_body}")


            message = MIMEMultipart()
            
            message["From"] = self.username
            message["To"] = to
            message["Subject"] = subject

            message.attach(
                MIMEText(
                    rendered_body,
                    "html",
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
                f"ERRO AO RENDERIZAR/ENVIAR TEMPLATE | to={to} | subject={subject}"
            )
            raise
