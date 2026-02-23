from abc import abstractmethod
from datetime import UTC, datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import func
from sqlmodel import Session, SQLModel, select

from app.domain.repositories.base import BaseRepository, EntityT

ModelT = TypeVar("ModelT", bound=SQLModel)


class SQLModelBaseRepository(BaseRepository[EntityT], Generic[ModelT, EntityT]):
    model_class: type[ModelT]

    def __init__(self, session: Session):
        self.session = session

    @abstractmethod
    def _to_entity(self, model: ModelT) -> EntityT: ...

    def get(self, entity_id: UUID) -> EntityT | None:
        obj = self.session.get(self.model_class, entity_id)
        return self._to_entity(obj) if obj else None

    def list(
        self,
        *,
        filters: dict[str, Any] | None = None,
        cursor: UUID | None = None,
        limit: int = 20,
        sort_field: str = "id",
        sort_desc: bool = True,
    ) -> list[EntityT]:
        stmt = select(self.model_class)
        if hasattr(self.model_class, "deleted_at"):
            stmt = stmt.where(self.model_class.deleted_at.is_(None))
        if filters:
            for field, value in filters.items():
                stmt = stmt.where(getattr(self.model_class, field) == value)
        col = getattr(self.model_class, sort_field)
        if cursor:
            stmt = stmt.where(col < cursor if sort_desc else col > cursor)
        stmt = stmt.order_by(col.desc() if sort_desc else col.asc())
        stmt = stmt.limit(limit)
        results = self.session.exec(stmt).all()
        return [self._to_entity(r) for r in results]

    def count(self, *, filters: dict[str, Any] | None = None) -> int:
        stmt = select(func.count()).select_from(self.model_class)
        if hasattr(self.model_class, "deleted_at"):
            stmt = stmt.where(self.model_class.deleted_at.is_(None))
        if filters:
            for field, value in filters.items():
                stmt = stmt.where(getattr(self.model_class, field) == value)
        return self.session.exec(stmt).one()

    def create(self, data: dict[str, Any]) -> EntityT:
        obj = self.model_class(**data)
        obj.created_at = datetime.now(UTC)
        obj.updated_at = datetime.now(UTC)
        self.session.add(obj)
        self.session.flush()
        self.session.refresh(obj)
        return self._to_entity(obj)

    def update(self, entity_id: UUID, data: dict[str, Any]) -> EntityT | None:
        obj = self.session.get(self.model_class, entity_id)
        obj.updated_at = datetime.now(UTC)
        if not obj:
            return None
        for key, value in data.items():
            setattr(obj, key, value)
        self.session.add(obj)
        self.session.flush()
        self.session.refresh(obj)
        return self._to_entity(obj)

    def soft_delete(self, entity_id: UUID) -> bool:
        obj = self.session.get(self.model_class, entity_id)
        if not obj:
            return False
        obj.deleted_at = datetime.now(UTC)
        self.session.add(obj)
        self.session.flush()
        return True

    def hard_delete(self, entity_id: UUID) -> bool:
        obj = self.session.get(self.model_class, entity_id)
        if not obj:
            return False
        self.session.delete(obj)
        self.session.flush()
        return True
