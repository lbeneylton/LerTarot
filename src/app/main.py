from fastapi import FastAPI

# Exeções
from app.core.exceptions import AppException

# Handlers
from app.core.handler import app_exception_handler

# Rotas
from api.auth import auther


app = FastAPI(
    title="Ler Tarot API",
    version="0.1.0",
    description="API da plataforma Ler_Tarot",
)


app.add_exception_handler(AppException, app_exception_handler)  # type: ignore

app.include_router(auther, tags=["Auth"])


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
