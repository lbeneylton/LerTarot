import pytest


@pytest.mark.anyio
async def test_health(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_create_user_client(async_client, user_payload):
    response = await async_client.post("/auth/register", json=user_payload)
    assert response.status_code == 201
    body = response.json()
    assert body["message"] == "Registro realizado com sucesso"


@pytest.mark.anyio
async def test_create_user_duplicate_email_returns_409(async_client, user_payload):
    await async_client.post("/auth/register", json=user_payload)
    response = await async_client.post("/auth/register", json=user_payload)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


@pytest.mark.anyio
async def test_create_user_invalid_password_returns_422(async_client, user_payload):
    user_payload["password"] = "curta"
    response = await async_client.post("/auth/register", json=user_payload)
    assert response.status_code == 422
