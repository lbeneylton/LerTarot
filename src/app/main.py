import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.handler import app_exception_handler
from app.api.v1.router import api_v1_router
from app.modules.emails.worker import email_worker
from app.infrastructure.logging.discord_handler import DiscordWebhookHandler
import logging

# Configuração global de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
discord_handler = DiscordWebhookHandler()
discord_handler.setLevel(logging.ERROR)
logger.addHandler(discord_handler)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Em ambiente Dockerizado, o worker roda no seu próprio container isolado
    # Portanto, não iniciamos mais ele em background aqui.
    yield


app = FastAPI(
    title="Ler Tarot API",
    version="0.1.0",
    summary="API da plataforma Ler Tarot",
    description="Plataforma de consultas de Tarot e agendamentos",
    lifespan=lifespan
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

app.include_router(api_v1_router)


@app.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/force-error", tags=["System"])
async def force_error() -> dict[str, str]:
    """Força um erro interno 500 para testar o envio de logs para o Discord."""
    logger.error("Este é um teste de log nível ERROR disparado pela rota /force-error.")
    raise ValueError("Teste de Erro Crítico 500 para o Webhook do Discord!")
