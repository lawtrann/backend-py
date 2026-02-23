from dataclasses import dataclass
from uuid import UUID

from app.application.decorators import transactional
from app.domain.entities.refresh_token import RefreshTokenEntity
from app.domain.entities.user import UserEntity
from app.domain.exceptions import InvalidAccessTokenError
from app.domain.repositories.refresh_token_repo import RefreshTokenRepository
from app.domain.repositories.user_repo import UserRepository
from app.domain.services.auth_service import AuthService
from app.domain.services.password_service import PasswordService
from app.domain.services.token_service import TokenService


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str


class RegisterUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        auth_service: AuthService,
        password_service: PasswordService,
    ):
        self.user_repo = user_repo
        self.auth_service = auth_service
        self.password_service = password_service

    @transactional
    def execute(self, username: str, email: str, password: str) -> UserEntity:
        self.auth_service.ensure_username_available(self.user_repo.get_by_username(username))
        self.auth_service.ensure_email_available(self.user_repo.get_by_email(email))
        entity = UserEntity(
            username=username,
            email=email,
            hashed_password=self.password_service.hash(password),
        )
        return self.user_repo.create(entity.model_dump())


class LoginUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        refresh_token_repo: RefreshTokenRepository,
        auth_service: AuthService,
        password_service: PasswordService,
        token_service: TokenService,
    ):
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo
        self.auth_service = auth_service
        self.password_service = password_service
        self.token_service = token_service

    @transactional
    def execute(self, username: str, password: str) -> TokenPair:
        user = self.auth_service.authenticate(
            self.user_repo.get_by_username(username), password, self.password_service.verify
        )
        access_token = self.token_service.create_access_token(user.id)
        refresh_token = self.token_service.generate_refresh_token()
        token_entity = RefreshTokenEntity(
            token_hash=self.token_service.hash_refresh_token(refresh_token),
            user_id=user.id,
            expires_at=self.token_service.get_refresh_token_expiry(),
        )
        self.refresh_token_repo.create(token_entity.model_dump())
        return TokenPair(access_token=access_token, refresh_token=refresh_token)


class RefreshUseCase:
    def __init__(
        self,
        refresh_token_repo: RefreshTokenRepository,
        auth_service: AuthService,
        token_service: TokenService,
    ):
        self.refresh_token_repo = refresh_token_repo
        self.auth_service = auth_service
        self.token_service = token_service

    @transactional
    def execute(self, refresh_token: str) -> TokenPair:
        old_hash = self.token_service.hash_refresh_token(refresh_token)
        token_data = self.auth_service.validate_refresh_token(
            self.refresh_token_repo.get_by_hash(old_hash)
        )
        self.refresh_token_repo.revoke_by_hash(old_hash)
        new_refresh = self.token_service.generate_refresh_token()
        new_token_entity = RefreshTokenEntity(
            token_hash=self.token_service.hash_refresh_token(new_refresh),
            user_id=token_data.user_id,
            expires_at=self.token_service.get_refresh_token_expiry(),
        )
        self.refresh_token_repo.create(new_token_entity.model_dump())
        access_token = self.token_service.create_access_token(token_data.user_id)
        return TokenPair(access_token=access_token, refresh_token=new_refresh)


class LogoutUseCase:
    def __init__(
        self,
        refresh_token_repo: RefreshTokenRepository,
        token_service: TokenService,
    ):
        self.refresh_token_repo = refresh_token_repo
        self.token_service = token_service

    @transactional
    def execute(self, refresh_token: str) -> None:
        self.refresh_token_repo.revoke_by_hash(
            self.token_service.hash_refresh_token(refresh_token)
        )


class GetCurrentUserUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        token_service: TokenService,
    ):
        self.user_repo = user_repo
        self.token_service = token_service

    def execute(self, access_token: str) -> UserEntity:
        payload = self.token_service.decode_access_token(access_token)
        user_id = UUID(payload["sub"])
        user = self.user_repo.get(user_id)
        if not user:
            raise InvalidAccessTokenError("User not found")
        return user
