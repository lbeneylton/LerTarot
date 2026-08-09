import pytest

from app.security import jwt_provider as jwt_module


@pytest.fixture(autouse=True)
def jwt_config(monkeypatch):
    monkeypatch.setattr(jwt_module, "SECRET_KEY", "chave-de-teste-jwt")
    monkeypatch.setattr(jwt_module, "ALGORITHM", "HS256")


def test_login_success(client, user_payload):
    # 1. Cadastra o usuário
    client.post("/users", json=user_payload)

    # 2. Faz o login
    login_payload = {
        "email": user_payload["email"],
        "password": user_payload["password"],
    }
    response = client.post("/auth/login", json=login_payload)

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

    # 3. Valida se o token gerado é decodificável e contém o payload correto
    decoded = jwt_module.decode_token(body["access_token"])
    assert decoded is not None
    assert "sub" in decoded
    assert decoded["user_type"] == "client"


def test_login_invalid_password(client, user_payload):
    # 1. Cadastra o usuário
    client.post("/users", json=user_payload)

    # 2. Tenta fazer o login com senha incorreta
    login_payload = {
        "email": user_payload["email"],
        "password": "senha_errada_123",
    }
    response = client.post("/auth/login", json=login_payload)

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"
    assert "incorretos" in body["error"]["message"]


def test_login_user_not_found(client):
    login_payload = {
        "email": "inexistente@example.com",
        "password": "senha1234",
    }
    response = client.post("/auth/login", json=login_payload)

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"
    assert "incorretos" in body["error"]["message"]


def test_login_invalid_payload(client):
    # E-mail inválido
    response = client.post(
        "/auth/login",
        json={"email": "email_invalido", "password": "senha1234"},
    )
    assert response.status_code == 422
