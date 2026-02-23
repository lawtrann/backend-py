from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


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
