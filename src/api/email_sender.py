from fastapi import APIRouter


email_sender = APIRouter(prefix="/emails", tags=["Emails"])


@email_sender.post("/")
def post_email():
    pass


@email_sender.get("/{email_id}")
def get_email(email_id: str):
    pass