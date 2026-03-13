"""Unit test configuration and shared fixtures."""
# Re-export fixtures from organized layer modules
from tests.unit.mock.repositories import (
    refresh_token_repo,
    user_repo,
)
from tests.unit.mock.services import (
    password_service,
    token_service,
)
from tests.unit.mock.uow import uow
from tests.unit.mock.use_cases import (
    get_current_user_use_case,
    login_use_case,
    logout_use_case,
    refresh_use_case,
    register_use_case,
)

__all__ = [
    # Repositories (domain layer)
    "user_repo",
    "refresh_token_repo",
    # Services (domain layer)
    "password_service",
    "token_service",
    # Unit of Work
    "uow",
    # Use cases (application layer)
    "register_use_case",
    "login_use_case",
    "refresh_use_case",
    "logout_use_case",
    "get_current_user_use_case",
]
