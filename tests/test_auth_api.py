import pytest


@pytest.mark.anyio
async def test_login_success(async_client, user_payload):
    await async_client.post("/auth/register", json=user_payload)

    login_payload = {
        "email_or_username": user_payload["email"],
        "password": user_payload["password"],
    }
    response = await async_client.post("/auth/login", json=login_payload)

    assert response.status_code == 202
    body = response.json()
    assert body["message"] == "Login realizado com sucesso"
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


@pytest.mark.anyio
async def test_login_invalid_password(async_client, user_payload):
    await async_client.post("/auth/register", json=user_payload)

    login_payload = {
        "email_or_username": user_payload["email"],
        "password": "senha_errada_123",
    }
    response = await async_client.post("/auth/login", json=login_payload)

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.anyio
async def test_login_user_not_found(async_client):
    login_payload = {
        "email_or_username": "inexistente@example.com",
        "password": "senha1234",
    }
    response = await async_client.post("/auth/login", json=login_payload)

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"
