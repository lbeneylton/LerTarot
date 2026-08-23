from fastapi import APIRouter, Depends, Header, BackgroundTasks, status, HTTPException

# from api.dependencies import get_email_service, verify_internal_token
from app.domains.emails.services import EmailService
from app.domains.emails.schemas import MessageRequest

# O roteador é protegido a nível de roteador:
# Todas as rotas neste arquivo exigem o header X-Internal-Token válido.
email_sender = APIRouter(
    prefix="/emails",
    tags=["Emails"],
    dependencies=[Depends(verify_internal_token)]
)


@email_sender.post("/", status_code=status.HTTP_202_ACCEPTED)
def post_email(
    data: MessageRequest,
    background_tasks: BackgroundTasks,
    x_idempotency_key: str | None = Header(default=None),
    email_service: EmailService = Depends(get_email_service)
) -> dict:
    """Enfileira um e-mail para envio assíncrono (Outbox Pattern).
    
    A rota é não bloqueante: ela valida/insere a mensagem e agenda a execução
    do worker em segundo plano de forma imediata.
    
    Garante idempotência se o header X-Idempotency-Key for fornecido.
    """
    try:
        email_message = email_service.enqueue_email(data, idempotency_key=x_idempotency_key)
        

        
        return {
            "message": "E-mail recebido e enfileirado para processamento",
            "message_id": email_message.message_id,
            "status": email_message.status.value
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@email_sender.get("/{message_id}", status_code=status.HTTP_200_OK)
def get_email(
    message_id: int,
    email_service: EmailService = Depends(get_email_service)
) -> dict:
    """Consulta o status e o histórico de tentativas de envio de um e-mail específico."""
    with email_service.uow as uow:
        msg = uow.emails.get_by_id(message_id)
        if not msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mensagem de e-mail não encontrada."
            )
        return {
            "message_id": msg.message_id,
            "to": msg.to,
            "subject": msg.subject,
            "template": msg.template,
            "status": msg.status.value,
            "attempts": msg.attempts,
            "next_retry_at": msg.next_retry_at,
            "created_at": msg.created_at,
            "sent_at": msg.sent_at,
            "error": msg.error
        }