"""Use case fixtures (application layer)."""
from unittest.mock import MagicMock

import pytest

from app.application.auth import (
    GetCurrentUserUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshUseCase,
    RegisterUseCase,
)
from app.core.context import session_ctx


@pytest.fixture(autouse=True)
def _mock_session():
    """Set a mock session in context so @transactional works in unit tests."""
    token = session_ctx.set(MagicMock())
    yield
    session_ctx.reset(token)


@pytest.fixture
def register_use_case(user_repo, auth_service, password_service):
    """RegisterUseCase with mocked dependencies."""
    return RegisterUseCase(
        user_repo=user_repo,
        auth_service=auth_service,
        password_service=password_service,
    )


@pytest.fixture
def login_use_case(user_repo, refresh_token_repo, auth_service, password_service, token_service):
    """LoginUseCase with mocked dependencies."""
    return LoginUseCase(
        user_repo=user_repo,
        refresh_token_repo=refresh_token_repo,
        auth_service=auth_service,
        password_service=password_service,
        token_service=token_service,
    )


@pytest.fixture
def refresh_use_case(refresh_token_repo, auth_service, token_service):
    """RefreshUseCase with mocked dependencies."""
    return RefreshUseCase(
        refresh_token_repo=refresh_token_repo,
        auth_service=auth_service,
        token_service=token_service,
    )


@pytest.fixture
def logout_use_case(refresh_token_repo, token_service):
    """LogoutUseCase with mocked dependencies."""
    return LogoutUseCase(
        refresh_token_repo=refresh_token_repo,
        token_service=token_service,
    )


@pytest.fixture
def get_current_user_use_case(user_repo, token_service):
    """GetCurrentUserUseCase with mocked dependencies."""
    return GetCurrentUserUseCase(
        user_repo=user_repo,
        token_service=token_service,
    )
