import pytest
from pydantic import ValidationError

from app.schemas.auth import RegisterRequest


def _valid_data(**overrides):
    defaults = {"username": "validuser", "email": "user@example.com", "password": "securepass1"}
    return {**defaults, **overrides}


class TestRegisterRequest:
    def test_valid_request(self):
        # Act
        req = RegisterRequest(**_valid_data())

        # Assert
        assert req.username == "validuser"

    def test_username_min_length(self):
        # Act & Assert
        with pytest.raises(ValidationError):
            RegisterRequest(**_valid_data(username="ab"))

    def test_username_max_length(self):
        # Act & Assert
        with pytest.raises(ValidationError):
            RegisterRequest(**_valid_data(username="a" * 51))

    def test_username_pattern_rejects_special_chars(self):
        # Act & Assert
        with pytest.raises(ValidationError):
            RegisterRequest(**_valid_data(username="user@name"))

    def test_username_pattern_allows_hyphens_underscores(self):
        # Act
        req = RegisterRequest(**_valid_data(username="valid_user-1"))

        # Assert
        assert req.username == "valid_user-1"

    def test_password_min_length(self):
        # Act & Assert
        with pytest.raises(ValidationError):
            RegisterRequest(**_valid_data(password="short"))

    def test_password_max_length(self):
        # Act & Assert
        with pytest.raises(ValidationError):
            RegisterRequest(**_valid_data(password="a" * 129))

    def test_invalid_email(self):
        # Act & Assert
        with pytest.raises(ValidationError):
            RegisterRequest(**_valid_data(email="not-an-email"))
