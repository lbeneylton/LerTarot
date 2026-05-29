def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_user_client(client, user_payload):
    response = client.post("/users", json=user_payload)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == user_payload["name"]
    assert body["email"] == user_payload["email"]
    assert body["user_type"] == "client"
    assert "user_id" in body
    assert "created_at" in body


def test_create_user_reader(client):
    response = client.post(
        "/users",
        json={
            "name": "Tarólogo",
            "email": "taro@example.com",
            "password": "senha1234",
            "user_type": "reader",
            "bio": "Especialista em arcanos maiores",
        },
    )

    assert response.status_code == 201
    assert response.json()["user_type"] == "reader"


def test_create_user_duplicate_email_returns_409(client, user_payload):
    client.post("/users", json=user_payload)
    response = client.post("/users", json=user_payload)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


def test_create_user_invalid_password_returns_422(client, user_payload):
    user_payload["password"] = "curta"
    response = client.post("/users", json=user_payload)
    assert response.status_code == 422
