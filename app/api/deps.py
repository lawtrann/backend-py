from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.api.security_container import Password, Token
from app.api.sqlmodel_container import UoW, UserRepo
from app.application.auth import (
    GetCurrentUserUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshUseCase,
    RegisterUseCase,
)
from app.core.context import set_user_id
from app.domain.entities.user import UserEntity

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ── Auth primitives ──────────────────────────────────────────────
AccessToken = Annotated[str, Depends(oauth2_scheme)]
LoginForm = Annotated[OAuth2PasswordRequestForm, Depends()]


# ── Use case factories ───────────────────────────────────────────
def _register_use_case(uow: UoW, password: Password) -> RegisterUseCase:
    return RegisterUseCase(uow=uow, password_service=password)


def _login_use_case(uow: UoW, password: Password, token_svc: Token) -> LoginUseCase:
    return LoginUseCase(uow=uow, password_service=password, token_service=token_svc)


def _refresh_use_case(uow: UoW, token_svc: Token) -> RefreshUseCase:
    return RefreshUseCase(uow=uow, token_service=token_svc)


def _logout_use_case(uow: UoW, token_svc: Token) -> LogoutUseCase:
    return LogoutUseCase(uow=uow, token_service=token_svc)


def get_current_user(
    access_token: AccessToken, user_repo: UserRepo, token_svc: Token,
) -> UserEntity:
    use_case = GetCurrentUserUseCase(
        user_repo=user_repo, token_service=token_svc,
    )
    user = use_case.execute(access_token)
    set_user_id(user.id)
    return user


# ── Annotated exports for routers ────────────────────────────────
Register = Annotated[RegisterUseCase, Depends(_register_use_case)]
Login = Annotated[LoginUseCase, Depends(_login_use_case)]
Refresh = Annotated[RefreshUseCase, Depends(_refresh_use_case)]
Logout = Annotated[LogoutUseCase, Depends(_logout_use_case)]
CurrentUser = Annotated[UserEntity, Depends(get_current_user)]
