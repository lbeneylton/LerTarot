import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Exceções
from app.core.exceptions import AppException

# Handlers
from app.core.handler import app_exception_handler

# Rotas
from api.auth import auth_router
from api.forgot_password import forgot_router
from api.email_verify import verify_router
# from api.email_sender import email_sender

# Worker
from providers.email_sender.worker import email_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicia o worker
    worker_task = asyncio.create_task(email_worker.start())

    try:
        yield
    finally:
       # Finaliza o worker no shutdown da aplicação
        email_worker.stop()
        await worker_task 



app = FastAPI(
    title="Ler Tarot API",
    version="0.1.0",
    summary="API da plataforma Ler Tarot",
    description="Catalógos e agendamentos",
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
# app.include_router(email_sender)


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
