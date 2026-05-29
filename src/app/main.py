from fastapi import FastAPI

from app.core.exceptions import AppException
from app.core.handler import app_exception_handler
from app.users.router import router as users_router

app = FastAPI(
    title="LerTarot API",
    version="0.1.0",
    description="API da plataforma LerTarot",
)

app.add_exception_handler(AppException, app_exception_handler)
app.include_router(users_router, prefix="/users", tags=["users"])


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
