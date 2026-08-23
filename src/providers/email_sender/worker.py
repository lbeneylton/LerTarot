import asyncio
import logging

from datetime import datetime, timezone, timedelta

from app.db.connection import SessionLocal
from app.db.uow import SqlAlchemyUnitOfWork
from app.domains.emails.models import MessageStatus

from providers.email_sender.get_sender import get_sender


logger = logging.getLogger("emails.worker")


class EmailWorker:
    def __init__(
        self,
        interval_seconds: int = 10,
        max_attempts: int = 5,
    ) -> None:
        self.interval_seconds = interval_seconds
        self.max_attempts = max_attempts
        self.email_sender = get_sender()
        self.running = False

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
                logger.exception("ERRO NO LOOP PRINCIPAL DO EMAIL WORKER")

                await asyncio.sleep(self.interval_seconds)

    def stop(self) -> None:
        self.running = False
        logger.info( "Background Email Worker parando...")

    async def process_emails(self) -> int:
        processed_count = 0

        # =====================================================
        # 1. PRIMEIRA UNIDADE DE TRABALHO
        #
        # Responsabilidade:
        # - buscar e-mails
        # - reservar e-mails
        # - COMMIT da reserva
        # =====================================================

        session = SessionLocal()

        try:
            uow = SqlAlchemyUnitOfWork(session)  # type: ignore

            logger.debug("Buscando e-mails pendentes...")

            with uow:
                pending_messages = (
                    uow.emails
                    .get_pending_emails_for_processing(
                        limit=10
                    )
                )

                if not pending_messages:
                    logger.debug("Sem e-mails pendentes")
                    return 0

                logger.info(f"Worker encontrou {len(pending_messages)} e-mails para processar.")
                for msg in pending_messages:
                    logger.info(
                        f"Reservando e-mail {msg.message_id} | "
                        f"template={msg.template} |" 
                        f"status atual={msg.status}"
                    )

                    msg.status = (MessageStatus.PROCESSING)
                    uow.emails.save(msg)

        except Exception:
            logger.exception(
                "ERRO AO BUSCAR/RESERVAR E-MAILS"
            )

            return 0

        # =====================================================
        # 2. PROCESSAMENTO INDIVIDUAL
        #
        # Cada e-mail possui:
        #
        # Session própria
        # UoW próprio
        # Transação própria
        # =====================================================

        for msg in pending_messages:

            try:
                logger.info("Processando e-mail {msg.message_id}")
                sub_session = SessionLocal()
                sub_uow = SqlAlchemyUnitOfWork(sub_session)  # type: ignore

                with sub_uow:

                    # =========================================
                    # Busca novamente usando a NOVA SESSION
                    # =========================================

                    db_msg = (
                        sub_uow.emails
                        .get_by_id(
                            msg.message_id
                        )
                    )

                    if not db_msg:
                        logger.error(f"E-mail {msg.message_id} não encontrado no banco.")
                        continue


                    # =========================================
                    # ENVIO
                    # =========================================

                    try:
                        logger.info(
                            "Chamando EmailSender.send() "
                            f"para e-mail {db_msg.message_id}..."
                        )

                        self.email_sender.send(
                            to=db_msg.to,
                            subject=db_msg.subject,
                            body=db_msg.body
                        )

                        # =====================================
                        # SUCESSO
                        # =====================================

                        db_msg.status = (
                            MessageStatus.SENT
                        )

                        db_msg.sent_at = (
                            datetime.now(timezone.utc)
                        )

                        db_msg.error = None

                        logger.info(f"E-mail {db_msg.message_id} enviado com sucesso.")

                    except Exception as send_err:

                        # =====================================
                        # ERRO NO ENVIO
                        # =====================================

                        logger.exception(
                            f"ERRO AO ENVIAR E-MAIL {db_msg.message_id} |" 
                            f"to={db_msg.to}"
                        )

                        db_msg.attempts += 1

                        error_msg = (
                            f"{type(send_err).__name__}: "
                            f"{str(send_err)}"
                        )

                        db_msg.error = error_msg

                        # =====================================
                        # RETRY
                        # =====================================

                        if (db_msg.attempts < self.max_attempts):
                            db_msg.status = (
                                MessageStatus.RETRY
                            )

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
                                "E-mail %s falhou. "
                                "Tentativa %s/%s. "
                                "Retry em %s segundos. "
                                "Erro: %s",
                                db_msg.message_id,
                                db_msg.attempts,
                                self.max_attempts,
                                backoff_seconds,
                                error_msg,
                            )

                        # =====================================
                        # FALHA DEFINITIVA
                        # =====================================

                        else:
                            db_msg.status = (
                                MessageStatus.FAILED
                            )

                            logger.error(
                                "E-mail %s falhou "
                                "definitivamente após %s "
                                "tentativas. Erro: %s",
                                db_msg.message_id,
                                db_msg.attempts,
                                error_msg,
                            )

                    # =========================================
                    # PERSISTE RESULTADO
                    # =========================================

                    sub_uow.emails.save(db_msg)

                    processed_count += 1

                # =============================================
                # Ao sair do `with sub_uow`:
                #
                # sucesso -> COMMIT
                # erro    -> ROLLBACK
                # sempre  -> CLOSE
                #
                # Portanto NÃO fazemos:
                #
                # sub_session.close()
                # =============================================

            except Exception:
                logger.exception(
                    "ERRO AO PROCESSAR E-MAIL %s",
                    msg.message_id,
                )

                # O erro de um e-mail não derruba
                # o processamento dos próximos.

                continue

        return processed_count


email_worker = EmailWorker()
