from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from uuid import UUID

EntityT = TypeVar("EntityT")


class BaseRepository(ABC, Generic[EntityT]):
    @abstractmethod
    def get(self, entity_id: UUID) -> EntityT | None: ...

    @abstractmethod
    def list(
        self,
        *,
        filters: dict[str, Any] | None = None,
        cursor: UUID | None = None,
        limit: int = 20,
        sort_field: str = "id",
        sort_desc: bool = True,
    ) -> list[EntityT]: ...

    @abstractmethod
    def count(self, *, filters: dict[str, Any] | None = None) -> int: ...

    @abstractmethod
    def create(self, data: dict[str, Any]) -> EntityT: ...

    @abstractmethod
    def update(self, entity_id: UUID, data: dict[str, Any]) -> EntityT | None: ...

    @abstractmethod
    def soft_delete(self, entity_id: UUID) -> bool: ...

    @abstractmethod
    def hard_delete(self, entity_id: UUID) -> bool: ...
