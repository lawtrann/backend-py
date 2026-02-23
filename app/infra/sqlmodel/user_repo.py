from sqlmodel import select

from app.domain.entities.user import UserEntity
from app.domain.repositories.user_repo import UserRepository
from app.infra.db.models import Users
from app.infra.sqlmodel.base import SQLModelBaseRepository


class SQLModelUserRepository(SQLModelBaseRepository[Users, UserEntity], UserRepository):
    model_class = Users

    def _to_entity(self, user: Users) -> UserEntity:
        return UserEntity.model_validate(user, from_attributes=True)

    def get_by_username(self, username: str) -> UserEntity | None:
        stmt = select(Users).where(Users.username == username)
        user = self.session.exec(stmt).first()
        return self._to_entity(user) if user else None

    def get_by_email(self, email: str) -> UserEntity | None:
        stmt = select(Users).where(Users.email == email)
        user = self.session.exec(stmt).first()
        return self._to_entity(user) if user else None
