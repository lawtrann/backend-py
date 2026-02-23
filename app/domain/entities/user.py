from collections.abc import Callable
from uuid import UUID

from pydantic import BaseModel, Field
from uuid_utils import uuid7 as _uuid7

from app.domain.exceptions import InactiveAccountError


class UserEntity(BaseModel):
    id: UUID = Field(default_factory=lambda: UUID(bytes=_uuid7().bytes))
    username: str
    email: str
    hashed_password: str
    is_active: bool = True

    def ensure_active(self) -> None:
        if not self.is_active:
            raise InactiveAccountError("User account is inactive")

    def verify_password(self, plain_password: str, verify_fn: Callable[[str, str], bool]) -> bool:
        return verify_fn(plain_password, self.hashed_password)
