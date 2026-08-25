from fastapi import APIRouter, Depends, Header, status, HTTPException

from app.modules.emails.services import EmailService
from app.modules.emails.schemas import MessageRequest, MessageResponse
from app.api.dependencies import get_email_service, verify_internal_token

email_router = APIRouter(
    prefix="/emails",
    tags=["Emails"],
    dependencies=[Depends(verify_internal_token)]
)


@email_router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def post_email(
    data: MessageRequest,
    x_idempotency_key: str | None = Header(default=None),
    email_service: EmailService = Depends(get_email_service)
) -> dict:
    try:
        email_message = await email_service.enqueue_email(data, idempotency_key=x_idempotency_key)
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


@email_router.get("/{message_id}", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def get_email(
    message_id: int,
    email_service: EmailService = Depends(get_email_service)
) -> MessageResponse:
    async with email_service.uow as uow:
        msg = await uow.emails.get_by_id(message_id)
        if not msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mensagem de e-mail não encontrada."
            )
        return MessageResponse(
            message_id=msg.message_id,
            to=msg.to,
            subject=msg.subject,
            template=msg.template,
            body=msg.body,
            status=msg.status.value,
            attempts=msg.attempts,
            next_retry_at=msg.next_retry_at,
            created_at=msg.created_at,
            sent_at=msg.sent_at,
            error=msg.error,
        )
