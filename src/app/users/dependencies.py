from fastapi import Depends

# Session para tipagem
from sqlalchemy.orm import Session
from app.db.connection import get_session

from app.users.repo import UserRepo
from app.users.services import UserService

# hashes e Jwt
from app.security.hasher import Argon2Hasher
from app.security.jwt_provider import JwtTokenService


def get_user_repo(session: Session = Depends(get_session)) -> UserRepo:
    return UserRepo(session)


def get_user_service(repo: UserRepo = Depends(get_user_repo)) -> UserService:
    hasher = Argon2Hasher()
    token_provider = JwtTokenService()
    return UserService(repo, hasher, token_provider)
