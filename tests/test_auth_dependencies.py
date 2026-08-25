import pytest
from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, RoleChecker
from app.modules.users.models import User, UserRole
from app.main import app

dummy_auth_router = APIRouter()


@dummy_auth_router.get("/me")
async def route_me(user: User = Depends(get_current_user)):
    return {"user_id": str(user.user_id), "role": user.role.value}


@dummy_auth_router.get("/admin-only")
async def route_admin_only(user: User = Depends(RoleChecker([UserRole.ADMIN]))):
    return {"success": True}


@dummy_auth_router.get("/reader-or-admin")
async def route_reader_or_admin(
    user: User = Depends(RoleChecker([UserRole.READER, UserRole.ADMIN]))
):
    return {"success": True}


app.include_router(dummy_auth_router, prefix="/test-auth")


@pytest.mark.anyio
async def test_get_current_user_missing_token(async_client):
    res = await async_client.get("/test-auth/me")
    assert res.status_code == 401
    assert "ausente ou inválido" in res.json()["error"]["message"]


@pytest.mark.anyio
async def test_get_current_user_invalid_token(async_client):
    headers = {"Authorization": "Bearer token_invalido_qualquer"}
    res = await async_client.get("/test-auth/me", headers=headers)
    assert res.status_code == 401
