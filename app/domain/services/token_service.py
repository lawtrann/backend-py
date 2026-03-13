from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domain.entities.refresh_token import RefreshTokenEntity


class TokenService(ABC):
    @abstractmethod
    def create_access_token(self, user_id: UUID) -> str: ...

    @abstractmethod
    def decode_access_token(self, token: str) -> dict: ...

    @abstractmethod
    def generate_refresh_token(self) -> str: ...

    @abstractmethod
    def hash_refresh_token(self, token: str) -> str: ...

    @abstractmethod
    def get_refresh_token_expiry(self) -> datetime: ...

    @abstractmethod
    def create_token_pair(self, user_id: UUID) -> tuple[str, str, RefreshTokenEntity]:
        """Returns (access_token, raw_refresh_token, refresh_token_entity)."""
        ...
