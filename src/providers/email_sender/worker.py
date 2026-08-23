import asyncio
import logging

from datetime import datetime, timezone, timedelta

from app.db.connection import SessionLocal
from app.db.uow import SqlAlchemyUnitOfWork
from app.domains.emails.models import MessageStatus

from providers.email_sender.get_sender import get_sender


logger = logging.getLogger("emails.worker")


# 1. Worker marca PROCESSING
# 2. Worker chama provider
# 3. Provider aceita e envia o e-mail
# 4. Worker morre
# 5. Banco continua PROCESSING
# 6. Timeout transforma em RETRY
# 7. Novo worker envia novamente


class EmailWorker:
    def __init__(
        self,
        interval_seconds: int = 10,
        max_attempts: int = 5,
        processing_timeout_seconds: int = 300,
    ) -> None:
        self.interval_seconds = interval_seconds
        self.max_attempts = max_attempts
        self.processing_timeout_seconds = processing_timeout_seconds
        
        self.email_sender = get_sender()
        self.running = False




    # =========================================================
    # START
    # =========================================================
    async def start(self) -> None:
        self.running = True

        logger.info("Background Email Worker iniciado...")

        while self.running:
            try:
                processed_count = await self.process_emails()

                if processed_count > 0:
                    await asyncio.sleep(0.5)
                else:
                    await asyncio.sleep(
                        self.interval_seconds
                    )

            except Exception:
                logger.exception(
                    "ERRO NO LOOP PRINCIPAL "
                    "DO EMAIL WORKER"
                )

                await asyncio.sleep(
                    self.interval_seconds
                )


    # =========================================================
    # STOP
    # =========================================================
    def stop(self) -> None:
        self.running = False
        logger.info( "Background Email Worker parando...")

  
  
  
  
    # =========================================================
    # PROCESS EMAILS
    # =========================================================
    async def process_emails(self) -> int:
        # -----------------------------------------------------
        # 1. Recupera mensagens travadas
        # -----------------------------------------------------     
        self.recover_stuck_emails()
        

        # -----------------------------------------------------
        # 2. Reserva novas mensagens
        # -----------------------------------------------------
        pending_message_ids = (
            self.reserve_emails()
        )

        if not pending_message_ids:
            return 0
        

        # -----------------------------------------------------
        # 3. Processa individualmente
        # -----------------------------------------------------
        processed_count = 0
        
        for message_id in pending_message_ids:

            try:

                success = await self.process_single_email(
                    message_id
                )

                if success:
                    processed_count += 1

            except Exception:
                logger.exception(
                    f"ERRO AO PROCESSAR E-MAIL {message_id}"
                )

        return processed_count


    # =========================================================
    # RECOVER STUCK EMAILS
    # =========================================================

    def recover_stuck_emails(self) -> int:

        session = SessionLocal()
        uow = SqlAlchemyUnitOfWork(session)  # type: ignore
        try:
            with uow:
                recovered_count = (
                    uow.emails
                    .recover_stuck_processing_emails(
                        timeout_seconds=(
                            self.processing_timeout_seconds
                        )
                    )
                )

                if recovered_count > 0:

                    logger.warning(
                        f"{recovered_count} e-mails PROCESSING "
                        "foram recuperados para RETRY."
                    )

                return recovered_count

        except Exception:
            logger.exception(
                "ERRO AO RECUPERAR E-MAILS "
                "PROCESSING TRAVADOS"
            )
            return 0



    # =========================================================
    # RESERVE EMAILS
    # =========================================================

    def reserve_emails(self) -> list[int]:
        # =====================================================
        # PRIMEIRA UNIDADE DE TRABALHO
        #
        # Responsabilidade:
        # - buscar e-mails
        # - reservar e-mails
        # - COMMIT da reserva
        # =====================================================
        
        session = SessionLocal()

        try:

            uow = SqlAlchemyUnitOfWork(session)  # type: ignore

            with uow:

                logger.debug("Buscando e-mails pendentes...")

                pending_messages = (
                    uow.emails
                    .get_pending_emails_for_processing(
                        limit=10
                    )
                )

                if not pending_messages:

                    logger.debug("Sem e-mails pendentes.")

                    return []

                now = datetime.now(
                    timezone.utc
                )

                message_ids = []

                logger.info(
                    f"Worker encontrou {len(pending_messages)} e-mails "
                    "para processar."
                )

                for msg in pending_messages:

                    logger.info(
                        "Reservando e-mail {msg.message_id} | "
                        "template= {msg.body} | "
                        "status atual= {msg.status}"
                    )

                    msg.status = (MessageStatus.PROCESSING)
                    msg.processing_started_at = now
                    msg.next_retry_at = None
                    uow.emails.save(msg)
                    message_ids.append(msg.message_id)

                return message_ids

        except Exception:

            logger.exception(
                "ERRO AO BUSCAR/RESERVAR "
                "E-MAILS"
            )

            return []



    # =========================================================
    # PROCESS SINGLE EMAIL
    # =========================================================

    async def process_single_email(
        self,
        message_id: int,
    ) -> bool:
        
        # =====================================================
        # PROCESSAMENTO INDIVIDUAL
        #
        # Cada e-mail possui:
        #
        # Session própria
        # UoW próprio
        # Transação própria
        # =====================================================

        session = SessionLocal()
        uow = SqlAlchemyUnitOfWork(session)  # type: ignore

        with uow:
            # =========================================
            # Busca novamente usando a NOVA SESSION
            # =========================================
            db_msg = (
                uow.emails
                .get_by_id(message_id)
            )


            if not db_msg:
                logger.error(
                    f"E-mail {message_id} não encontrado "
                    "no banco."
                )

                return False

            # -------------------------------------------------
            # Segurança adicional:
            # somente PROCESSING pode ser processado aqui.
            # -------------------------------------------------

            if (db_msg.status!= MessageStatus.PROCESSING):
                logger.warning(
                    f"E-mail {message_id} não está mais "
                    f"PROCESSING. Status={db_msg.status}"
                )
                return False


            # -------------------------------------------------
            # ENVIO
            # -------------------------------------------------

            try:
                logger.info(
                    "Chamando EmailSender.send_template() "
                    f"para e-mail {db_msg.message_id}..."
                )

                self.email_sender.send_template(
                    to=db_msg.to,
                    subject=db_msg.subject,
                    template=f"{db_msg.body}.html",
                    variable=dict(
                        db_msg.variables or {}
                    ),
                )

                # ---------------------------------------------
                # SUCESSO
                # ---------------------------------------------

                db_msg.status = (MessageStatus.SENT)
                db_msg.sent_at = (
                    datetime.now(timezone.utc)
                )
                db_msg.processing_started_at = None
                db_msg.next_retry_at = None
                db_msg.error = None
                logger.info(
                    f"E-mail {db_msg.message_id} enviado "
                    "com sucesso."
                )

            except Exception as send_err:
                # ---------------------------------------------
                # ERRO NO ENVIO
                # ---------------------------------------------
                logger.exception(
                    f"ERRO AO ENVIAR E-MAIL {db_msg.message_id} "
                    f"| to={db_msg.to}"
                )

                db_msg.attempts += 1

                error_msg = (
                    f"{type(send_err).__name__}: "
                    f"{str(send_err)}"
                )

                db_msg.error = error_msg
                db_msg.processing_started_at = None

                # ---------------------------------------------
                # RETRY
                # ---------------------------------------------

                if (db_msg.attempts < self.max_attempts):

                    db_msg.status = (MessageStatus.RETRY)

                    backoff_seconds = (
                        2 ** db_msg.attempts
                    )

                    db_msg.next_retry_at = (
                        datetime.now(
                            timezone.utc
                        )
                        + timedelta(
                            seconds=backoff_seconds
                        )
                    )

                    logger.warning(
                        f"E-mail {db_msg.message_id} falhou. "
                        f"Tentativa {db_msg.attempts}/{self.max_attempts}. "
                        f"Retry ems {backoff_seconds} segundos. "
                        f"Erro: {error_msg}"
                    )

                # ---------------------------------------------
                # FALHA DEFINITIVA
                # ---------------------------------------------

                else:

                    db_msg.status = (MessageStatus.FAILED)
                    db_msg.next_retry_at = None

                    logger.error(
                        f"E-mail {db_msg.message_id} falhou "
                        f"definitivamente após "
                        f"{db_msg.attempts} tentativas. "
                        f"Erro: {error_msg}"
                    )

            # -------------------------------------------------
            # PERSISTE
            # -------------------------------------------------
            uow.emails.save(db_msg)
            return True

email_worker = EmailWorker()
