from app.api.provider import Singleton
from app.domain.services.password_service import PasswordService
from app.domain.services.token_service import TokenService
from app.infra.security.argon2_password_service import Argon2PasswordService
from app.infra.security.jwt_token_service import JwtTokenService

Password = Singleton(PasswordService, Argon2PasswordService())
Token = Singleton(TokenService, JwtTokenService())
