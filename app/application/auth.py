from dataclasses import dataclass
from uuid import UUID

from app.core.uow import UnitOfWork
from app.domain.entities.user import UserEntity
from app.domain.exceptions import (
    DuplicateEmailError,
    DuplicateUsernameError,
    InvalidAccessTokenError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from app.domain.repositories.refresh_token_repo import RefreshTokenRepository
from app.domain.repositories.user_repo import UserRepository
from app.domain.services.password_service import PasswordService
from app.domain.services.token_service import TokenService


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str


class RegisterUseCase:
    def __init__(self, uow: UnitOfWork, password_service: PasswordService):
        self.uow = uow
        self.password_service = password_service

    def execute(self, username: str, email: str, password: str) -> UserEntity:
        with self.uow:
            users = self.uow.repo(UserRepository)
            if users.get_by_username(username):
                raise DuplicateUsernameError("Username already taken")
            if users.get_by_email(email):
                raise DuplicateEmailError("Email already registered")
            entity = UserEntity(
                username=username,
                email=email,
                hashed_password=self.password_service.hash(password),
            )
            user = users.create(entity.model_dump())
            self.uow.commit()
            return user


class LoginUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        password_service: PasswordService,
        token_service: TokenService,
    ):
        self.uow = uow
        self.password_service = password_service
        self.token_service = token_service

    def execute(self, username: str, password: str) -> TokenPair:
        with self.uow:
            users = self.uow.repo(UserRepository)
            user = users.get_by_username(username)
            if not user or not user.verify_password(password, self.password_service.verify):
                raise InvalidCredentialsError("Invalid username or password")
            user.ensure_active()
            access_token, raw_refresh, token_entity = self.token_service.create_token_pair(user.id)
            self.uow.repo(RefreshTokenRepository).create(token_entity.model_dump())
            self.uow.commit()
            return TokenPair(access_token=access_token, refresh_token=raw_refresh)


class RefreshUseCase:
    def __init__(self, uow: UnitOfWork, token_service: TokenService):
        self.uow = uow
        self.token_service = token_service

    def execute(self, refresh_token: str) -> TokenPair:
        with self.uow:
            refresh_tokens = self.uow.repo(RefreshTokenRepository)
            old_hash = self.token_service.hash_refresh_token(refresh_token)
            token_data = refresh_tokens.get_by_hash(old_hash)
            if not token_data:
                raise InvalidRefreshTokenError("Invalid or expired refresh token")
            token_data.ensure_valid()
            refresh_tokens.revoke_by_hash(old_hash)
            access_token, raw_refresh, new_entity = self.token_service.create_token_pair(
                token_data.user_id
            )
            refresh_tokens.create(new_entity.model_dump())
            self.uow.commit()
            return TokenPair(access_token=access_token, refresh_token=raw_refresh)


class LogoutUseCase:
    def __init__(self, uow: UnitOfWork, token_service: TokenService):
        self.uow = uow
        self.token_service = token_service

    def execute(self, refresh_token: str) -> None:
        with self.uow:
            self.uow.repo(RefreshTokenRepository).revoke_by_hash(
                self.token_service.hash_refresh_token(refresh_token)
            )
            self.uow.commit()


class GetCurrentUserUseCase:
    def __init__(self, user_repo: UserRepository, token_service: TokenService):
        self.user_repo = user_repo
        self.token_service = token_service

    def execute(self, access_token: str) -> UserEntity:
        payload = self.token_service.decode_access_token(access_token)
        user_id = UUID(payload["sub"])
        user = self.user_repo.get(user_id)
        if not user:
            raise InvalidAccessTokenError("User not found")
        return user
