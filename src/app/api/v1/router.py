from fastapi import APIRouter

from app.api.v1.routers.auth import auth_router
from app.api.v1.routers.password_recovery import forgot_router
from app.api.v1.routers.email_verification import verify_router
from app.api.v1.routers.emails import email_router
from app.api.v1.routers.users import users_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(forgot_router)
api_v1_router.include_router(verify_router)
api_v1_router.include_router(email_router)
api_v1_router.include_router(users_router)
