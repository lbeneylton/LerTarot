import pytest

from app.security import jwt_provider as jwt_module


@pytest.fixture(autouse=True)
def jwt_config(monkeypatch):
    monkeypatch.setattr(jwt_module, "SECRET_KEY", "chave-de-teste-jwt")
    monkeypatch.setattr(jwt_module, "ALGORITHM", "HS256")


def test_create_and_decode_token():
    token = jwt_module.create_access_token({"sub": "user-1"})
    payload = jwt_module.decode_token(token)

    assert payload is not None
    assert payload["sub"] == "user-1"
    assert "exp" in payload


def test_decode_invalid_token():
    assert jwt_module.decode_token("token.invalido") is None
