from contextvars import ContextVar
from uuid import UUID

from uuid_utils import uuid7 as _uuid7

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
user_id_ctx: ContextVar[str] = ContextVar("user_id", default="")


def get_request_id() -> str:
    return request_id_ctx.get()


def set_request_id(value: str | None = None) -> None:
    request_id_ctx.set(value or str(UUID(bytes=_uuid7().bytes)))


def get_user_id() -> str:
    return user_id_ctx.get()


def set_user_id(value: UUID | str) -> None:
    user_id_ctx.set(str(value))
