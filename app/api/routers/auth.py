from fastapi import APIRouter, Cookie, Depends, Response, status

from app.api.deps import (
    CurrentUser,
    Login,
    LoginForm,
    Logout,
    Refresh,
    Register,
    get_current_user,
)
from app.core.config import settings
from app.schemas.auth import RegisterRequest, TokenResponse, UserResponse

_REFRESH_COOKIE = "refresh_token"
_REFRESH_COOKIE_MAX_AGE = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

router = APIRouter(prefix="/auth", tags=["auth"])
protected_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, use_case: Register):
    user = use_case.execute(
        username=body.username, email=body.email, password=body.password,
    )
    return UserResponse(
        id=user.id, username=user.username,
        email=user.email, is_active=user.is_active,
    )


@router.post("/login", response_model=TokenResponse)
def login(response: Response, form_data: LoginForm, use_case: Login):
    result = use_case.execute(
        username=form_data.username, password=form_data.password,
    )
    _set_refresh_cookie(response, result.refresh_token)
    return TokenResponse(access_token=result.access_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    response: Response,
    use_case: Refresh,
    refresh_token: str = Cookie(alias=_REFRESH_COOKIE),
):
    result = use_case.execute(refresh_token=refresh_token)
    _set_refresh_cookie(response, result.refresh_token)
    return TokenResponse(access_token=result.access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    use_case: Logout,
    refresh_token: str = Cookie(alias=_REFRESH_COOKIE),
):
    use_case.execute(refresh_token=refresh_token)
    response.delete_cookie(key=_REFRESH_COOKIE, path="/api/v1/auth")


@protected_router.get("/me", response_model=UserResponse)
def me(current_user: CurrentUser):
    return UserResponse(
        id=current_user.id, username=current_user.username,
        email=current_user.email, is_active=current_user.is_active,
    )


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE, value=token, httponly=True,
        secure=settings.COOKIE_SECURE, samesite="lax",
        path="/api/v1/auth", max_age=_REFRESH_COOKIE_MAX_AGE,
    )
