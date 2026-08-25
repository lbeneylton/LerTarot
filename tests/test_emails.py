import pytest
from fastapi import status

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.db.uow import SqlAlchemyUnitOfWork
from app.domains.emails.models import EmailMessage, MessageStatus
from app.domains.emails.services import EmailService
from app.domains.emails.schemas import MessageRequest
from app.domains.emails.worker import EmailWorker


@pytest.mark.anyio
async def test_enqueue_email_and_idempotency() -> None:
    async with AsyncSessionLocal() as session:
        uow = SqlAlchemyUnitOfWork(session)
        email_service = EmailService(uow)
        
        req = MessageRequest(
            to="test@example.com",
            subject="Assunto Teste",
            template="verify_email",
            variables={"user_name": "Teste", "code": "123456"}
        )
        key = "unique-idempotency-key-123"
        
        msg1 = await email_service.enqueue_email(req, idempotency_key=key)
        assert msg1.message_id is not None
        assert msg1.status == MessageStatus.PENDING
        assert msg1.idempotency_key == key
        assert msg1.body == "verify_email"
        
        msg2 = await email_service.enqueue_email(req, idempotency_key=key)
        assert msg1.message_id == msg2.message_id


@pytest.mark.anyio
async def test_worker_processing() -> None:
    async with AsyncSessionLocal() as session:
        uow = SqlAlchemyUnitOfWork(session)
        email_service = EmailService(uow)
        
        req = MessageRequest(
            to="worker@example.com",
            subject="Assunto Worker",
            template="verify_email",
            variables={"user_name": "Worker", "code": "654321"}
        )
        await email_service.enqueue_email(req, idempotency_key="worker-key")
        
        worker = EmailWorker(max_attempts=3)
        processed = await worker.process_emails()
        assert processed == 1

        async with uow:
            msg = await uow.emails.get_by_idempotency_key("worker-key")
            assert msg is not None
            assert msg.status == MessageStatus.SENT
            assert msg.sent_at is not None


@pytest.mark.anyio
async def test_api_emails_access_control(async_client) -> None:
    response = await async_client.post("/emails/", json={
        "to": "test@example.com",
        "subject": "Teste API",
        "template": "verify_email"
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    response = await async_client.post(
        "/emails/",
        json={
            "to": "test@example.com",
            "subject": "Teste API",
            "template": "verify_email"
        },
        headers={"X-Internal-Token": "token-incorreto"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    valid_token = settings.internal_api_key
    response = await async_client.post(
        "/emails/",
        json={
            "to": "test@example.com",
            "subject": "Teste API",
            "template": "verify_email"
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
