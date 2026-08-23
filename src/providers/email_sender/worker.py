import asyncio
import logging

from datetime import datetime, timezone, timedelta

from app.db.connection import SessionLocal
from app.db.uow import SqlAlchemyUnitOfWork
from app.domains.emails.models import MessageStatus

from providers.email_sender.get_sender import get_sender

logger = logging.getLogger("emails.worker")


class EmailWorker:
    def __init__(self, interval_seconds: int = 10, max_attempts: int = 5) -> None:
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
                    # Se processou e-mails, roda novamente com pequeno delay
                    await asyncio.sleep(0.5)
                else:
                    await asyncio.sleep(self.interval_seconds)
            except Exception as e:
                logger.error(f"Erro no loop do Worker de E-mails: {str(e)}")
                await asyncio.sleep(self.interval_seconds)

    def stop(self) -> None:
        self.running = False
        logger.info("Background Email Worker parando...")

    async def process_emails(self) -> int:
        session = SessionLocal()
        uow = SqlAlchemyUnitOfWork(session)
        
        try:
            with uow:
                # 1. Busca e-mails pendentes aplicando SKIP LOCKED para concorrência
                pending_messages = uow.emails.get_pending_emails_for_processing(limit=10)
                if not pending_messages:
                    return 0
                
                logger.info(f"Worker encontrou {len(pending_messages)} e-mails para processar.")
                
                # Marca todos os e-mails reservados como PROCESSING e commita imediatamente
                for msg in pending_messages:
                    msg.status = MessageStatus.PROCESSING
                    uow.emails.save(msg)
            
            # 2. Processa cada e-mail em uma transação individual para evitar locks longos
            processed_count = 0
            for msg in pending_messages:
                sub_session = SessionLocal()
                sub_uow = SqlAlchemyUnitOfWork(sub_session)
                
                try:
                    with sub_uow:
                        db_msg = sub_uow.emails.get_by_id(msg.message_id)
                        if not db_msg:
                            continue
                        
                        try:
                            # Envia o e-mail de fato
                            self.email_sender.send(
                                to=db_msg.to,
                                subject=db_msg.subject,
                                body=db_msg.body
                            )
                            
                            db_msg.status = MessageStatus.SENT
                            db_msg.sent_at = datetime.now(timezone.utc)
                            db_msg.error = None
                            logger.info(f"E-mail {db_msg.message_id} enviado com sucesso para {db_msg.to}.")
                        except Exception as send_err:
                            db_msg.attempts += 1
                            error_msg = f"{type(send_err).__name__}: {str(send_err)}"
                            db_msg.error = error_msg
                            
                            # Lógica de retry com backoff exponencial
                            if db_msg.attempts < self.max_attempts:
                                db_msg.status = MessageStatus.RETRY
                                backoff_minutes = 2 ** db_msg.attempts
                                db_msg.next_retry_at = datetime.now(timezone.utc) + timedelta(minutes=backoff_minutes)
                                logger.warning(
                                    f"Falha ao enviar e-mail {db_msg.message_id} para {db_msg.to} (Tentativa {db_msg.attempts}/{self.max_attempts}). "
                                    f"Agendado retry em {backoff_minutes} min. Erro: {error_msg}"
                                )
                            else:
                                db_msg.status = MessageStatus.FAILED
                                logger.error(
                                    f"E-mail {db_msg.message_id} para {db_msg.to} falhou definitivamente. Erro: {error_msg}"
                                )
                                
                        sub_uow.emails.save(db_msg)
                        processed_count += 1
                except Exception as inner_err:
                    logger.error(f"Erro ao processar mensagem {msg.message_id}: {str(inner_err)}")
                finally:
                    sub_session.close()
            
            return processed_count
            
        except Exception as e:
            logger.error(f"Erro ao buscar/reservar e-mails: {str(e)}")
            return 0
        finally:
            session.close()


email_worker = EmailWorker()
