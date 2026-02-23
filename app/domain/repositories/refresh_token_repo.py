from abc import abstractmethod
from uuid import UUID

from app.domain.entities.refresh_token import RefreshTokenEntity
from app.domain.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshTokenEntity]):
    @abstractmethod
    def get_by_hash(self, token_hash: str) -> RefreshTokenEntity | None: ...

    @abstractmethod
    def revoke_by_hash(self, token_hash: str) -> None: ...

    @abstractmethod
    def revoke_all_for_user(self, user_id: UUID) -> None: ...
