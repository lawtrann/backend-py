"""Fake Unit of Work for unit tests."""
import pytest

from app.core.uow import UnitOfWork
from app.domain.repositories.base import BaseRepository
from app.domain.repositories.refresh_token_repo import RefreshTokenRepository
from app.domain.repositories.user_repo import UserRepository


class FakeUnitOfWork(UnitOfWork):
    def __init__(self, repos: dict[type, BaseRepository]):
        self._repos = repos
        self.committed = False
        self.rolled_back = False

    def repo(self, repo_type: type[BaseRepository]) -> BaseRepository:
        return self._repos[repo_type]

    def __enter__(self) -> "FakeUnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rolled_back = True

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


@pytest.fixture
def uow(user_repo, refresh_token_repo):
    """FakeUnitOfWork with mock repos."""
    return FakeUnitOfWork(repos={
        UserRepository: user_repo,
        RefreshTokenRepository: refresh_token_repo,
    })
