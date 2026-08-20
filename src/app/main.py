from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Exeções
from app.core.exceptions import AppException

# Handlers
from app.core.handler import app_exception_handler

# Rotas
from api.auth import auth_router
from api.email_verify import email_router
from api.email_sender import email_sender


app = FastAPI(
    title="Ler Tarot API",
    version="0.1.0",
    summary="API da plataforma Ler Tarot",
    description="Catalógos e agendamentos",
)

origins = [
    "https://agendamento-frontend-alpha.vercel.app",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(AppException, app_exception_handler)  # type: ignore

app.include_router(auth_router)
app.include_router(email_router)
app.include_router(email_sender)


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
