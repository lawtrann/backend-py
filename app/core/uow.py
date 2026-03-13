from abc import ABC, abstractmethod
from typing import TypeVar

from app.domain.repositories.base import BaseRepository

RepoT = TypeVar("RepoT", bound=BaseRepository)


class UnitOfWork(ABC):
    @abstractmethod
    def repo(self, repo_type: type[RepoT]) -> RepoT: ...

    @abstractmethod
    def __enter__(self) -> "UnitOfWork": ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...
