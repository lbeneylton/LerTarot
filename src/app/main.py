import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.exceptions import AppException
from app.core.handler import app_exception_handler

from app.modules.auth.router import auth_router
from app.modules.password_recovery.router import forgot_router
from app.modules.email_verification.router import verify_router
from app.modules.emails.router import email_router
from app.modules.emails.worker import email_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    description="Catálogos, agendamentos e e-mails",
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

app.include_router(auth_router)
app.include_router(forgot_router)
app.include_router(verify_router)
app.include_router(email_router)


@app.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
