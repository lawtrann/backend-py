"""Mock repository fixtures."""
from unittest.mock import create_autospec

import pytest

from app.domain.repositories.refresh_token_repo import RefreshTokenRepository
from app.domain.repositories.user_repo import UserRepository


@pytest.fixture
def user_repo():
    """Mock UserRepository (ABC)."""
    return create_autospec(UserRepository, instance=True)


@pytest.fixture
def refresh_token_repo():
    """Mock RefreshTokenRepository (ABC)."""
    return create_autospec(RefreshTokenRepository, instance=True)
