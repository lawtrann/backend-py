import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from app.core.config import settings
from app.domain.entities.refresh_token import RefreshTokenEntity
from app.domain.exceptions import InvalidAccessTokenError
from app.domain.services.token_service import TokenService


class JwtTokenService(TokenService):
    def create_access_token(self, user_id: UUID) -> str:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload = {"sub": str(user_id), "exp": expire}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    def decode_access_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise InvalidAccessTokenError("Access token has expired")
        except jwt.InvalidTokenError:
            raise InvalidAccessTokenError("Invalid access token")

    def generate_refresh_token(self) -> str:
        return secrets.token_urlsafe(32)

    def hash_refresh_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def get_refresh_token_expiry(self) -> datetime:
        return datetime.now(UTC) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    def create_token_pair(self, user_id: UUID) -> tuple[str, str, RefreshTokenEntity]:
        access_token = self.create_access_token(user_id)
        raw_refresh = self.generate_refresh_token()
        entity = RefreshTokenEntity(
            token_hash=self.hash_refresh_token(raw_refresh),
            user_id=user_id,
            expires_at=self.get_refresh_token_expiry(),
        )
        return access_token, raw_refresh, entity
