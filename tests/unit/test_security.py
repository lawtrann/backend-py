import time
from datetime import UTC

import jwt
import pytest
from uuid_utils import uuid7

from app.core.config import settings
from app.domain.exceptions import InvalidAccessTokenError
from app.infra.security.argon2_password_service import Argon2PasswordService as PasswordService
from app.infra.security.jwt_token_service import JwtTokenService as TokenService


class TestPasswordHashing:
    def setup_method(self):
        self.password_service = PasswordService()

    def test_hash_and_verify(self):
        # Arrange
        password = "SecurePass123!"

        # Act
        hashed = self.password_service.hash(password)

        # Assert
        assert hashed != password
        assert self.password_service.verify(password, hashed)

    def test_wrong_password_fails(self):
        # Arrange
        hashed = self.password_service.hash("correct")

        # Assert
        assert not self.password_service.verify("wrong", hashed)

    def test_different_hashes_for_same_password(self):
        # Act
        h1 = self.password_service.hash("same")
        h2 = self.password_service.hash("same")

        # Assert
        assert h1 != h2  # Salted


class TestJWT:
    def setup_method(self):
        self.token_service = TokenService()

    def test_create_and_decode(self):
        # Arrange
        test_id = uuid7()

        # Act
        token = self.token_service.create_access_token(user_id=test_id)
        payload = self.token_service.decode_access_token(token)

        # Assert
        assert payload["sub"] == str(test_id)
        assert "exp" in payload

    def test_expired_token_raises(self):
        # Arrange
        payload = {"sub": str(uuid7()), "exp": time.time() - 10}
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        # Act & Assert
        with pytest.raises(InvalidAccessTokenError):
            self.token_service.decode_access_token(token)

    def test_invalid_token_raises(self):
        # Act & Assert
        with pytest.raises(InvalidAccessTokenError):
            self.token_service.decode_access_token("garbage.token.here")

    def test_wrong_secret_raises(self):
        # Arrange
        token = jwt.encode({"sub": str(uuid7()), "exp": time.time() + 300}, "wrong-key", algorithm="HS256")

        # Act & Assert
        with pytest.raises(InvalidAccessTokenError):
            self.token_service.decode_access_token(token)


class TestRefreshToken:
    def setup_method(self):
        self.token_service = TokenService()

    def test_generate_is_unique(self):
        # Act
        t1 = self.token_service.generate_refresh_token()
        t2 = self.token_service.generate_refresh_token()

        # Assert
        assert t1 != t2
        assert len(t1) > 20

    def test_hash_is_deterministic(self):
        # Arrange
        token = "some-token"

        # Assert
        assert self.token_service.hash_refresh_token(token) == self.token_service.hash_refresh_token(token)

    def test_hash_differs_for_different_tokens(self):
        # Assert
        assert self.token_service.hash_refresh_token("a") != self.token_service.hash_refresh_token("b")

    def test_expiry_is_in_future(self):
        # Act
        from datetime import datetime
        expiry = self.token_service.get_refresh_token_expiry()

        # Assert
        assert expiry > datetime.now(UTC)
