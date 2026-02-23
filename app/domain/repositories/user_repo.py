from abc import abstractmethod

from app.domain.entities.user import UserEntity
from app.domain.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserEntity]):
    @abstractmethod
    def get_by_username(self, username: str) -> UserEntity | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> UserEntity | None: ...
