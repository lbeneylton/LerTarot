from datetime import timedelta

from fastapi import Response

from app.core.config import settings


ACCESS_PATH = "/"
REFRESH_PATH = "/auth/refresh"


class CookieManager:
    def __init__(
        self,
        access_age: int,
        refresh_age: int,
        secure: bool = True,
    ) -> None:
        self.access_age = access_age
        self.refresh_age = refresh_age
        self.secure = secure

    def set_auth_cookies(
        self,
        response: Response,
        access_token: str,
        refresh_token: str,
    ) -> None:
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=self.secure,
            samesite="lax",
            max_age=self.access_age,
            path=ACCESS_PATH,
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=self.secure,
            samesite="lax",
            max_age=self.refresh_age,
            path=REFRESH_PATH,
        )

    def clear_auth_cookies(self, response: Response) -> None:
        response.delete_cookie(
            key="access_token",
            path=ACCESS_PATH,
        )

        response.delete_cookie(
            key="refresh_token",
            path=REFRESH_PATH,
        )


ACCESS_MAX_AGE = int(
    timedelta(
        minutes=settings.access_expire_minutes
    ).total_seconds()
)

REFRESH_MAX_AGE = int(
    timedelta(
        days=settings.refresh_expire_days
    ).total_seconds()
)


cookie_manager = CookieManager(
    access_age=ACCESS_MAX_AGE,
    refresh_age=REFRESH_MAX_AGE,
    secure=False,  # True em produção com HTTPS
)
