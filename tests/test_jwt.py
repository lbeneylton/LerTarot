import pytest

from app.security.jwt_provider import get_token_provider
from app.core.exceptions import UnauthorizedError


def test_create_and_decode_token():
    provider = get_token_provider()
    token = provider.create_access_token(user_id=1, version=1)
    payload = provider.decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "1"
    assert payload["token_version"] == "1"
    assert "exp" in payload


def test_decode_invalid_token():
    provider = get_token_provider()
    with pytest.raises(UnauthorizedError):
        provider.decode_access_token("token.invalido")
