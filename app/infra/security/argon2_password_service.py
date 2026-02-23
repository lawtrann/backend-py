from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.domain.services.password_service import PasswordService

pwd_context = PasswordHash((Argon2Hasher(),))


class Argon2PasswordService(PasswordService):
    def hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)
