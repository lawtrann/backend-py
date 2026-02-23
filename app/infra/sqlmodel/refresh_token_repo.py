from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import select

from app.domain.entities.refresh_token import RefreshTokenEntity
from app.domain.repositories.refresh_token_repo import RefreshTokenRepository
from app.infra.db.models import RefreshTokens as RefreshToken
from app.infra.sqlmodel.base import SQLModelBaseRepository


class SQLModelRefreshTokenRepository(SQLModelBaseRepository[RefreshToken, RefreshTokenEntity], RefreshTokenRepository):
    model_class = RefreshToken

    def _to_entity(self, token: RefreshToken) -> RefreshTokenEntity:
        return RefreshTokenEntity.model_validate(token, from_attributes=True)

    def get_by_hash(self, token_hash: str) -> RefreshTokenEntity | None:
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
        )
        token = self.session.exec(stmt).first()
        return self._to_entity(token) if token else None

    def revoke_by_hash(self, token_hash: str) -> None:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        token = self.session.exec(stmt).first()
        if token:
            token.revoked_at = datetime.now(UTC)
            self.session.add(token)
            self.session.flush()

    def revoke_all_for_user(self, user_id: UUID) -> None:
        stmt = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
        )
        tokens = self.session.exec(stmt).all()
        now = datetime.now(UTC)
        for token in tokens:
            token.revoked_at = now
            self.session.add(token)
        self.session.flush()
