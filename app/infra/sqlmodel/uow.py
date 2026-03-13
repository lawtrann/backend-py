from sqlalchemy import Engine

from app.core.uow import UnitOfWork
from app.domain.repositories.base import BaseRepository
from app.domain.repositories.refresh_token_repo import RefreshTokenRepository
from app.domain.repositories.user_repo import UserRepository
from app.infra.db.session import _acquire_session
from app.infra.sqlmodel.refresh_token_repo import SQLModelRefreshTokenRepository
from app.infra.sqlmodel.user_repo import SQLModelUserRepository

_REPO_REGISTRY: list[tuple[type, type]] = [
    (UserRepository, SQLModelUserRepository),
    (RefreshTokenRepository, SQLModelRefreshTokenRepository),
]


class SQLModelUnitOfWork(UnitOfWork):
    def __init__(self, engine: Engine):
        self._engine = engine

    def __enter__(self) -> "SQLModelUnitOfWork":
        self._session = _acquire_session(self._engine)
        self._repos = {abc: impl(self._session) for abc, impl in _REPO_REGISTRY}
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self._session.rollback()
        self._session.close()

    def repo(self, repo_type: type[BaseRepository]) -> BaseRepository:
        return self._repos[repo_type]

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
