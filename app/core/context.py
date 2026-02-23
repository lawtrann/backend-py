from contextvars import ContextVar, Token
from uuid import UUID

from sqlmodel import Session
from uuid_utils import uuid7 as _uuid7

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
user_id_ctx: ContextVar[str] = ContextVar("user_id", default="")
session_ctx: ContextVar[Session | None] = ContextVar("session", default=None)


def get_request_id() -> str:
    return request_id_ctx.get()


def set_request_id(value: str | None = None) -> None:
    request_id_ctx.set(value or str(UUID(bytes=_uuid7().bytes)))


def get_user_id() -> str:
    return user_id_ctx.get()


def set_user_id(value: UUID | str) -> None:
    user_id_ctx.set(str(value))


def get_session() -> Session:
    session = session_ctx.get()
    if session is None:
        raise RuntimeError("No database session in context")
    return session


def set_session(session: Session) -> Token[Session | None]:
    return session_ctx.set(session)


def reset_session(token: Token[Session | None]) -> None:
    session_ctx.reset(token)
