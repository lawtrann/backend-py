from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, Field
from uuid_utils import uuid7 as _uuid7

from app.domain.exceptions import InvalidRefreshTokenError


class RefreshTokenEntity(BaseModel):
    id: UUID = Field(default_factory=lambda: UUID(bytes=_uuid7().bytes))
    token_hash: str
    user_id: UUID
    expires_at: datetime
    revoked_at: datetime | None = None

    def ensure_valid(self) -> None:
        if self.revoked_at is not None:
            raise InvalidRefreshTokenError("Invalid or expired refresh token")
        if self.expires_at < datetime.now(UTC):
            raise InvalidRefreshTokenError("Invalid or expired refresh token")
