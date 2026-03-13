"""Use case fixtures (application layer)."""
import pytest

from app.application.auth import (
    GetCurrentUserUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshUseCase,
    RegisterUseCase,
)


@pytest.fixture
def register_use_case(uow, password_service):
    """RegisterUseCase with mocked dependencies."""
    return RegisterUseCase(uow=uow, password_service=password_service)


@pytest.fixture
def login_use_case(uow, password_service, token_service):
    """LoginUseCase with mocked dependencies."""
    return LoginUseCase(
        uow=uow, password_service=password_service, token_service=token_service,
    )


@pytest.fixture
def refresh_use_case(uow, token_service):
    """RefreshUseCase with mocked dependencies."""
    return RefreshUseCase(uow=uow, token_service=token_service)


@pytest.fixture
def logout_use_case(uow, token_service):
    """LogoutUseCase with mocked dependencies."""
    return LogoutUseCase(uow=uow, token_service=token_service)


@pytest.fixture
def get_current_user_use_case(user_repo, token_service):
    """GetCurrentUserUseCase with mocked dependencies."""
    return GetCurrentUserUseCase(user_repo=user_repo, token_service=token_service)
