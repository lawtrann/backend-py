from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from uuid_utils import uuid7 as _uuid7

from app.domain.entities.refresh_token import RefreshTokenEntity
from app.domain.entities.user import UserEntity
from app.domain.exceptions import (
    DuplicateEmailError,
    DuplicateUsernameError,
    InvalidAccessTokenError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)


class TestRegisterUseCase:
    def test_success(self, register_use_case, user_repo, password_service):
        # Arrange
        user_repo.get_by_username.return_value = None
        user_repo.get_by_email.return_value = None
        password_service.hash.return_value = "hashed_password123"
        expected_user = UserEntity(
            username="alice", email="alice@example.com", hashed_password="hashed_password123"
        )
        user_repo.create.return_value = expected_user

        # Act
        user = register_use_case.execute("alice", "alice@example.com", "password123")

        # Assert
        assert user.username == "alice"
        assert user.email == "alice@example.com"
        assert user.hashed_password == "hashed_password123"
        assert isinstance(user.id, UUID)
        password_service.hash.assert_called_once_with("password123")
        user_repo.create.assert_called_once()

    def test_duplicate_username(self, register_use_case, user_repo):
        # Arrange
        existing = UserEntity(username="alice", email="alice@example.com", hashed_password="x")
        user_repo.get_by_username.return_value = existing

        # Act & Assert
        with pytest.raises(DuplicateUsernameError, match="Username already taken"):
            register_use_case.execute("alice", "other@example.com", "pw")

    def test_duplicate_email(self, register_use_case, user_repo):
        # Arrange
        user_repo.get_by_username.return_value = None
        existing = UserEntity(username="bob", email="alice@example.com", hashed_password="x")
        user_repo.get_by_email.return_value = existing

        # Act & Assert
        with pytest.raises(DuplicateEmailError, match="Email already registered"):
            register_use_case.execute("bob", "alice@example.com", "pw")


class TestLoginUseCase:
    def test_success(self, login_use_case, user_repo, password_service, token_service):
        # Arrange
        user = UserEntity(
            username="alice", email="alice@example.com", hashed_password="hashed_secret"
        )
        user_repo.get_by_username.return_value = user
        password_service.verify.return_value = True
        token_service.create_access_token.return_value = f"access_{user.id}"
        token_service.generate_refresh_token.return_value = "new_raw_refresh"
        token_service.hash_refresh_token.return_value = "hashed_refresh"
        token_service.get_refresh_token_expiry.return_value = datetime.now(UTC) + timedelta(days=7)

        # Act
        result = login_use_case.execute("alice", "secret")

        # Assert
        assert result.access_token == f"access_{user.id}"
        assert result.refresh_token == "new_raw_refresh"

    def test_wrong_password(self, login_use_case, user_repo, password_service):
        # Arrange
        user = UserEntity(
            username="alice", email="alice@example.com", hashed_password="hashed_secret"
        )
        user_repo.get_by_username.return_value = user
        password_service.verify.return_value = False

        # Act & Assert
        with pytest.raises(InvalidCredentialsError, match="Invalid username or password"):
            login_use_case.execute("alice", "wrong")


class TestRefreshUseCase:
    def test_success(self, refresh_use_case, refresh_token_repo, token_service):
        # Arrange
        user_id = UUID(bytes=_uuid7().bytes)
        expires = datetime.now(UTC) + timedelta(days=7)
        token_entity = RefreshTokenEntity(
            token_hash="hashed_old_raw", user_id=user_id, expires_at=expires
        )
        token_service.hash_refresh_token.side_effect = lambda t: f"hashed_{t}"
        refresh_token_repo.get_by_hash.return_value = token_entity
        token_service.generate_refresh_token.return_value = "new_raw_refresh"
        token_service.create_access_token.return_value = f"access_{user_id}"
        token_service.get_refresh_token_expiry.return_value = expires

        # Act
        result = refresh_use_case.execute("old_raw")

        # Assert
        assert result.access_token == f"access_{user_id}"
        assert result.refresh_token == "new_raw_refresh"
        refresh_token_repo.revoke_by_hash.assert_called_once_with("hashed_old_raw")

    def test_invalid_token(self, refresh_use_case, refresh_token_repo, token_service):
        # Arrange
        token_service.hash_refresh_token.return_value = "hashed_bad_token"
        refresh_token_repo.get_by_hash.return_value = None

        # Act & Assert
        with pytest.raises(InvalidRefreshTokenError, match="Invalid or expired"):
            refresh_use_case.execute("bad_token")


class TestLogoutUseCase:
    def test_revokes_token(self, logout_use_case, refresh_token_repo, token_service):
        # Arrange
        token_service.hash_refresh_token.return_value = "hashed_raw_tok"

        # Act
        logout_use_case.execute("raw_tok")

        # Assert
        refresh_token_repo.revoke_by_hash.assert_called_once_with("hashed_raw_tok")


class TestGetCurrentUserUseCase:
    def test_success(self, get_current_user_use_case, user_repo, token_service):
        # Arrange
        user = UserEntity(
            username="alice", email="alice@example.com", hashed_password="hashed_pw"
        )
        token_service.decode_access_token.return_value = {"sub": str(user.id)}
        user_repo.get.return_value = user

        # Act
        result = get_current_user_use_case.execute("some_token")

        # Assert
        assert result.username == "alice"

    def test_invalid_token(self, get_current_user_use_case, token_service):
        # Arrange
        token_service.decode_access_token.side_effect = InvalidAccessTokenError(
            "Invalid access token"
        )

        # Act & Assert
        with pytest.raises(InvalidAccessTokenError, match="Invalid access token"):
            get_current_user_use_case.execute("garbage")

    def test_user_not_found(self, get_current_user_use_case, user_repo, token_service):
        # Arrange
        fake_id = UUID(bytes=_uuid7().bytes)
        token_service.decode_access_token.return_value = {"sub": str(fake_id)}
        user_repo.get.return_value = None

        # Act & Assert
        with pytest.raises(InvalidAccessTokenError, match="User not found"):
            get_current_user_use_case.execute("some_token")
