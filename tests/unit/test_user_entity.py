import pytest

from app.domain.entities.user import UserEntity
from app.domain.exceptions import InactiveAccountError


def _make_user(**overrides) -> UserEntity:
    defaults = {
        "username": "alice",
        "email": "alice@example.com",
        "hashed_password": "hashed",
        "is_active": True,
    }
    defaults.update(overrides)
    return UserEntity(**defaults)


class TestEnsureActive:
    def test_active_user_passes(self):
        # Arrange
        user = _make_user(is_active=True)

        # Act & Assert
        user.ensure_active()

    def test_inactive_user_raises(self):
        # Arrange
        user = _make_user(is_active=False)

        # Act & Assert
        with pytest.raises(InactiveAccountError, match="User account is inactive"):
            user.ensure_active()


class TestVerifyPassword:
    def test_correct_password(self):
        # Arrange
        user = _make_user(hashed_password="hashed")

        # Assert
        assert user.verify_password("hashed", lambda p, h: p == h) is True

    def test_wrong_password(self):
        # Arrange
        user = _make_user(hashed_password="hashed")

        # Assert
        assert user.verify_password("wrong", lambda p, h: p == h) is False
