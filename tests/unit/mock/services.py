"""Mock service fixtures."""
from unittest.mock import create_autospec

import pytest

from app.domain.services.auth_service import AuthService
from app.domain.services.password_service import PasswordService
from app.domain.services.token_service import TokenService


@pytest.fixture
def auth_service():
    """Real AuthService (concrete, no mocking needed)."""
    return AuthService()


@pytest.fixture
def password_service():
    """Mock PasswordService (ABC)."""
    return create_autospec(PasswordService, instance=True)


@pytest.fixture
def token_service():
    """Mock TokenService (ABC)."""
    return create_autospec(TokenService, instance=True)
