import pytest
from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user, RoleChecker
from app.users.enums import UserType
from app.users.models import User
from app.core.security import jwt as jwt_module


@pytest.fixture(autouse=True)
def jwt_config(monkeypatch):
    monkeypatch.setattr(jwt_module, "SECRET_KEY", "chave-de-teste-jwt")
    monkeypatch.setattr(jwt_module, "ALGORITHM", "HS256")


# Criamos rotas de teste protegidas para verificar as dependências
dummy_auth_router = APIRouter()


@dummy_auth_router.get("/me")
def route_me(user: User = Depends(get_current_user)):
    return {"user_id": str(user.user_id), "user_type": user.user_type.value}


@dummy_auth_router.get("/admin-only")
def route_admin_only(user: User = Depends(RoleChecker([UserType.admin]))):
    return {"success": True}


@dummy_auth_router.get("/reader-or-admin")
def route_reader_or_admin(
    user: User = Depends(RoleChecker([UserType.reader, UserType.admin]))
):
    return {"success": True}


@pytest.fixture
def auth_client(client):
    # Incluímos as rotas de teste temporariamente no app principal importado pelo conftest
    client.app.include_router(dummy_auth_router, prefix="/test-auth")
    return client


def test_get_current_user_success(auth_client, user_payload):
    # 1. Cadastra o usuário e faz login para obter o token
    auth_client.post("/users", json=user_payload)
    login_res = auth_client.post(
        "/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    token = login_res.json()["access_token"]

    # 2. Chama a rota protegida enviando o token no cabeçalho
    headers = {"Authorization": f"Bearer {token}"}
    res = auth_client.get("/test-auth/me", headers=headers)

    assert res.status_code == 200
    assert "user_id" in res.json()
    assert res.json()["user_type"] == "client"


def test_get_current_user_missing_token(auth_client):
    res = auth_client.get("/test-auth/me")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "UNAUTHORIZED"
    assert "ausente ou inválido" in res.json()["error"]["message"]


def test_get_current_user_invalid_token(auth_client):
    headers = {"Authorization": "Bearer token_invalido_qualquer"}
    res = auth_client.get("/test-auth/me", headers=headers)
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "UNAUTHORIZED"


def test_role_checker_permitted(auth_client, user_payload):
    # Criando um usuário reader
    user_payload["user_type"] = "reader"
    user_payload["email"] = "reader@example.com"
    auth_client.post("/users", json=user_payload)

    # Login
    login_res = auth_client.post(
        "/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Rota permitida para reader ou admin
    res = auth_client.get("/test-auth/reader-or-admin", headers=headers)
    assert res.status_code == 200
    assert res.json() == {"success": True}


def test_role_checker_forbidden(auth_client, user_payload):
    # Criando um usuário client
    user_payload["user_type"] = "client"
    user_payload["email"] = "client@example.com"
    auth_client.post("/users", json=user_payload)

    # Login
    login_res = auth_client.post(
        "/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Rota restrita a apenas admin (o cliente tenta acessar)
    res = auth_client.get("/test-auth/admin-only", headers=headers)
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "FORBIDDEN"
    assert "Acesso negado" in res.json()["error"]["message"]
