from collections.abc import Callable
from datetime import UTC, datetime

from app.domain.entities.refresh_token import RefreshTokenEntity
from app.domain.entities.user import UserEntity
from app.domain.exceptions import (
    DuplicateEmailError,
    DuplicateUsernameError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)


class AuthService:
    @staticmethod
    def ensure_username_available(existing_user: UserEntity | None) -> None:
        if existing_user:
            raise DuplicateUsernameError("Username already taken")

    @staticmethod
    def ensure_email_available(existing_user: UserEntity | None) -> None:
        if existing_user:
            raise DuplicateEmailError("Email already registered")

    @staticmethod
    def authenticate(
        user: UserEntity | None,
        password: str,
        verify_fn: Callable[[str, str], bool],
    ) -> UserEntity:
        if not user or not user.verify_password(password, verify_fn):
            raise InvalidCredentialsError("Invalid username or password")
        user.ensure_active()
        return user

    @staticmethod
    def validate_refresh_token( token: RefreshTokenEntity | None ) -> RefreshTokenEntity:
        if not token or token.revoked_at is not None:
            raise InvalidRefreshTokenError("Invalid or expired refresh token")
        expires = token.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)
        if expires < datetime.now(UTC):
            raise InvalidRefreshTokenError("Invalid or expired refresh token")
        return token
