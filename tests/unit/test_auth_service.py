from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from uuid_utils import uuid7 as _uuid7

from app.domain.entities.refresh_token import RefreshTokenEntity
from app.domain.entities.user import UserEntity
from app.domain.exceptions import (
    DuplicateEmailError,
    DuplicateUsernameError,
    InactiveAccountError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from app.domain.services.auth_service import AuthService


@pytest.fixture
def auth_service():
    return AuthService()


_TEST_USER_ID = UUID(bytes=_uuid7().bytes)


def _make_user(**overrides) -> UserEntity:
    defaults = {
        "id": _TEST_USER_ID,
        "username": "alice",
        "email": "alice@example.com",
        "hashed_password": "hashed",
        "is_active": True,
    }
    defaults.update(overrides)
    return UserEntity(**defaults)


def _make_token(**overrides) -> RefreshTokenEntity:
    defaults = {
        "token_hash": "hash1",
        "user_id": _TEST_USER_ID,
        "expires_at": datetime.now(UTC) + timedelta(days=7),
        "revoked_at": None,
    }
    defaults.update(overrides)
    return RefreshTokenEntity(**defaults)


class TestEnsureUsernameAvailable:
    def test_available(self, auth_service):
        # Act & Assert
        auth_service.ensure_username_available(None)

    def test_taken(self, auth_service):
        # Act & Assert
        with pytest.raises(DuplicateUsernameError, match="Username already taken"):
            auth_service.ensure_username_available(_make_user())


class TestEnsureEmailAvailable:
    def test_available(self, auth_service):
        # Act & Assert
        auth_service.ensure_email_available(None)

    def test_taken(self, auth_service):
        # Act & Assert
        with pytest.raises(DuplicateEmailError, match="Email already registered"):
            auth_service.ensure_email_available(_make_user())


class TestAuthenticate:
    def _verify(self, plain, hashed):
        return plain == hashed

    def test_success(self, auth_service):
        # Arrange
        user = _make_user()

        # Act
        result = auth_service.authenticate(user, "hashed", self._verify)

        # Assert
        assert result.username == "alice"

    def test_wrong_password(self, auth_service):
        # Arrange
        user = _make_user()

        # Act & Assert
        with pytest.raises(InvalidCredentialsError, match="Invalid username or password"):
            auth_service.authenticate(user, "wrong", self._verify)

    def test_nonexistent_user(self, auth_service):
        # Act & Assert
        with pytest.raises(InvalidCredentialsError, match="Invalid username or password"):
            auth_service.authenticate(None, "pw", self._verify)

    def test_inactive_user(self, auth_service):
        # Arrange
        user = _make_user(is_active=False)

        # Act & Assert
        with pytest.raises(InactiveAccountError, match="inactive"):
            auth_service.authenticate(user, "hashed", self._verify)


class TestValidateRefreshToken:
    def test_valid_token(self, auth_service):
        # Arrange
        token = _make_token()

        # Act
        result = auth_service.validate_refresh_token(token)

        # Assert
        assert result.user_id == _TEST_USER_ID

    def test_none_token(self, auth_service):
        # Act & Assert
        with pytest.raises(InvalidRefreshTokenError, match="Invalid or expired"):
            auth_service.validate_refresh_token(None)

    def test_revoked_token(self, auth_service):
        # Arrange
        token = _make_token(revoked_at=datetime.now(UTC))

        # Act & Assert
        with pytest.raises(InvalidRefreshTokenError, match="Invalid or expired"):
            auth_service.validate_refresh_token(token)

    def test_expired_token(self, auth_service):
        # Arrange
        token = _make_token(expires_at=datetime.now(UTC) - timedelta(hours=1))

        # Act & Assert
        with pytest.raises(InvalidRefreshTokenError, match="Invalid or expired"):
            auth_service.validate_refresh_token(token)

    def test_naive_datetime_treated_as_utc(self, auth_service):
        # Arrange
        naive_expires = (datetime.now(UTC) + timedelta(days=1)).replace(tzinfo=None)
        token = _make_token(expires_at=naive_expires)

        # Act
        result = auth_service.validate_refresh_token(token)

        # Assert
        assert result.user_id == _TEST_USER_ID
