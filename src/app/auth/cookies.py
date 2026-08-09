# app/auth/cookies.py

from fastapi import Response


ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"

ACCESS_MAX_AGE = 15 * 60
REFRESH_MAX_AGE = 7 * 24 * 60 * 60

ACCESS_PATH = "/"
REFRESH_PATH = "/auth/refresh"

# HTTPS
SECURE = False


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:
    response.set_cookie(
        key=ACCESS_COOKIE,
        value=access_token,
        httponly=True,
        secure=SECURE,
        samesite="lax",
        max_age=ACCESS_MAX_AGE,
        path=ACCESS_PATH,
    )

    response.set_cookie(
        key=REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=SECURE,
        samesite="lax",
        max_age=REFRESH_MAX_AGE,
        path=REFRESH_PATH,
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(
        key=ACCESS_COOKIE,
        path=ACCESS_PATH,
    )

    response.delete_cookie(
        key=REFRESH_COOKIE,
        path=REFRESH_PATH,
    )
