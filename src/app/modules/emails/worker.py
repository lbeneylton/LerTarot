import asyncio
import logging
from datetime import datetime, timezone, timedelta

from app.db.session import AsyncSessionLocal
from app.db.uow import SqlAlchemyUnitOfWork
from app.modules.emails.models import MessageStatus
from app.modules.emails.senders import get_sender

logger = logging.getLogger("emails.worker")


from app.infrastructure.notifications.discord_notifier import DiscordNotifier

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
        self.notifier = DiscordNotifier()
        self.running = False

    @property
    def email_sender(self):
        return get_sender()

    async def start(self) -> None:
        self.running = True
        logger.info("Background Email Worker iniciado (Async)...")

        while self.running:
            try:
                processed_count = await self.process_emails()
                if processed_count > 0:
                    await asyncio.sleep(0.5)
                else:
                    await asyncio.sleep(self.interval_seconds)
            except Exception:
                logger.exception("ERRO NO LOOP PRINCIPAL DO EMAIL WORKER")
                await asyncio.sleep(self.interval_seconds)

    def stop(self) -> None:
        self.running = False
        logger.info("Background Email Worker parando...")

    async def process_emails(self) -> int:
        await self.recover_stuck_emails()
        pending_ids = await self.reserve_emails()

        if not pending_ids:
            return 0

        processed_count = 0
        for message_id in pending_ids:
            try:
                success = await self.process_single_email(message_id)
                if success:
                    processed_count += 1
            except Exception:
                logger.exception(f"ERRO AO PROCESSAR E-MAIL {message_id}")

        return processed_count

    async def recover_stuck_emails(self) -> int:
        async with AsyncSessionLocal() as session:
            uow = SqlAlchemyUnitOfWork(session)
            try:
                async with uow:
                    recovered = await uow.emails.recover_stuck_processing_emails(
                        timeout_seconds=self.processing_timeout_seconds
                    )
                    if recovered > 0:
                        logger.warning(f"{recovered} e-mails PROCESSING recuperados para RETRY.")
                    return recovered
            except Exception:
                logger.exception("ERRO AO RECUPERAR E-MAILS PROCESSING TRAVADOS")
                return 0

    async def reserve_emails(self) -> list[int]:
        async with AsyncSessionLocal() as session:
            try:
                uow = SqlAlchemyUnitOfWork(session)
                async with uow:
                    pending_messages = await uow.emails.get_pending_emails_for_processing(limit=10)
                    if not pending_messages:
                        return []

                    now = datetime.now(timezone.utc)
                    message_ids = []
                    for msg in pending_messages:
                        msg.status = MessageStatus.PROCESSING
                        msg.processing_started_at = now
                        msg.next_retry_at = None
                        await uow.emails.save(msg)
                        message_ids.append(msg.message_id)

                    return message_ids
            except Exception:
                logger.exception("ERRO AO RESERVAR E-MAILS")
                return []

    async def process_single_email(self, message_id: int) -> bool:
        async with AsyncSessionLocal() as session:
            uow = SqlAlchemyUnitOfWork(session)
            async with uow:
                db_msg = await uow.emails.get_by_id(message_id)
                if not db_msg or db_msg.status != MessageStatus.PROCESSING:
                    return False

                try:
                    template_name = db_msg.body or "verify_email"

                    variables = dict(db_msg.variables or {})

                    try:
                        self.email_sender.send_template(
                            to=db_msg.to,
                            subject=db_msg.subject,
                            template_name=template_name,
                            variables=variables,
                        )
                    except Exception as t_err:
                        logger.exception(f"FALHA NO TEMPLATE HTML '{template_name}'. Enviando texto puro fallback. Erro: {t_err}")
                        self.email_sender.send_text(
                            to=db_msg.to,
                            subject=db_msg.subject,
                            body=str(db_msg.body),
                        )

                    db_msg.status = MessageStatus.SENT
                    db_msg.sent_at = datetime.now(timezone.utc)
                    db_msg.processing_started_at = None
                    db_msg.next_retry_at = None
                    db_msg.error = None
                    logger.info(f"E-mail {db_msg.message_id} enviado com sucesso.")
                    
                    # Dispara alerta de sucesso de envio via webhook em background
                    await self.notifier.notify_email_sent(to_email=db_msg.to, subject=db_msg.subject)

                except Exception as send_err:
                    db_msg.attempts += 1
                    error_msg = f"{type(send_err).__name__}: {str(send_err)}"
                    db_msg.error = error_msg
                    db_msg.processing_started_at = None

                    if db_msg.attempts < self.max_attempts:
                        db_msg.status = MessageStatus.RETRY
                        backoff = 2 ** db_msg.attempts
                        db_msg.next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=backoff)
                    else:
                        db_msg.status = MessageStatus.FAILED
                        db_msg.next_retry_at = None

                await uow.emails.save(db_msg)
                return True


email_worker = EmailWorker()
