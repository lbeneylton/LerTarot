import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.handler import app_exception_handler
from app.api.v1.router import api_v1_router
from app.modules.emails.worker import email_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Em modo local/dev, inicia o worker em segundo plano. Em produção, ele pode rodar via `cli.py`
    worker_task = asyncio.create_task(email_worker.start())
    try:
        yield
    finally:
        email_worker.stop()
        await worker_task


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
