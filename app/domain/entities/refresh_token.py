from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from uuid_utils import uuid7 as _uuid7


class RefreshTokenEntity(BaseModel):
    id: UUID = Field(default_factory=lambda: UUID(bytes=_uuid7().bytes))
    token_hash: str
    user_id: UUID
    expires_at: datetime
    revoked_at: datetime | None = None
