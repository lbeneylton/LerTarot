import pytest
from fastapi.testclient import TestClient
from fastapi import status

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.uow import SqlAlchemyUnitOfWork
from providers.emails.model import EmailMessage, MessageStatus
from providers.emails.services import EmailService
from providers.emails.schemas import MessageRequest
from providers.emails.worker import EmailWorker


def test_enqueue_email_and_idempotency() -> None:
    session = SessionLocal()
    uow = SqlAlchemyUnitOfWork(session)
    email_service = EmailService(uow)
    
    req = MessageRequest(
        to="test@example.com",
        subject="Assunto Teste",
        body="Olá, este é um corpo de teste."
    )
    key = "unique-idempotency-key-123"
    
    # 1. Primeira inserção
    msg1 = email_service.enqueue_email(req, idempotency_key=key)
    assert msg1.message_id is not None
    assert msg1.status == MessageStatus.PENDING
    assert msg1.idempotency_key == key
    
    # 2. Segunda inserção com mesma chave (deve retornar a mesma mensagem existente)
    msg2 = email_service.enqueue_email(req, idempotency_key=key)
    assert msg1.message_id == msg2.message_id
    
    # 3. Verifica se existe apenas 1 mensagem no banco
    with uow:
        db_messages = uow.emails.get_pending_emails_for_processing(limit=10)
        assert len(db_messages) == 1
    
    session.close()


@pytest.mark.anyio
async def test_worker_processing() -> None:
    session = SessionLocal()
    uow = SqlAlchemyUnitOfWork(session)
    email_service = EmailService(uow)
    
    req = MessageRequest(
        to="worker@example.com",
        subject="Assunto Worker",
        body="Corpo do worker"
    )
    email_service.enqueue_email(req, idempotency_key="worker-key")
    session.close()
    
    # Executa o processamento do worker (em ambiente de teste get_sender() usa o mock)
    worker = EmailWorker(max_attempts=3)
    processed = await worker.process_emails()
    assert processed == 1
    
    # Verifica o status atualizado no banco
    session = SessionLocal()
    uow = SqlAlchemyUnitOfWork(session)
    with uow:
        msg = uow.emails.get_by_idempotency_key("worker-key")
        assert msg is not None
        assert msg.status == MessageStatus.SENT
        assert msg.sent_at is not None
        assert msg.attempts == 0
    session.close()


def test_api_emails_access_control(client: TestClient) -> None:
    # 1. Sem o header de segurança exigido (FastAPI retorna 422 pela falta do parâmetro obrigatório)
    response = client.post("/emails/", json={
        "to": "test@example.com",
        "subject": "Teste API",
        "body": "Corpo"
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # 2. Com token incorreto (deve retornar 403)
    response = client.post(
        "/emails/",
        json={
            "to": "test@example.com",
            "subject": "Teste API",
            "body": "Corpo"
        },
        headers={"X-Internal-Token": "token-incorreto"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # 3. Com token válido (deve retornar 202)
    valid_token = settings.internal_api_key
    response = client.post(
        "/emails/",
        json={
            "to": "test@example.com",
            "subject": "Teste API",
            "body": "Corpo"
        },
        headers={
            "X-Internal-Token": valid_token,
            "X-Idempotency-Key": "api-key-idemp-1"
        }
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert "message_id" in data
    assert data["status"] == "PENDING"
