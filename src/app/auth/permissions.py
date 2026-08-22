# app/auth/dependencies.py

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.connection import get_session
from app.domains.users.models import User
from app.security.jwt_provider import get_token_provider


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_session),
    jwt_provider = Depends(get_token_provider)
) -> User:

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
        )

    payload = jwt_provider.decode_access_token(access_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    user = (
        db.query(User)
        .filter(User.user_id == int(user_id))
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
        )

    return user
