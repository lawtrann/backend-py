from collections.abc import Callable
from typing import Annotated

from fastapi import Depends


def Singleton[T](abstract: type[T], instance: T) -> type[T]:
    """App lifetime — same instance across all requests."""

    def provide() -> T:
        return instance

    provide.__name__ = f"singleton_{abstract.__name__}"
    provide.__qualname__ = provide.__name__
    return Annotated[abstract, Depends(provide)]  # type: ignore[return-value]


def RequestScope[T](abstract: type[T], create: Callable[..., T]) -> type[T]:
    """Request lifetime — one instance per request, reused if injected multiple times."""
    return Annotated[abstract, Depends(create)]  # type: ignore[return-value]


def NoScope[T](abstract: type[T], create: Callable[..., T]) -> type[T]:
    """Transient — new instance on every injection, even within the same request.

    Note: only the *top-level* dependency bypasses the cache.
    Sub-dependencies (e.g. get_db) are still cached per-request by FastAPI,
    which is usually the desired behaviour.
    """
    return Annotated[abstract, Depends(create, use_cache=False)]  # type: ignore[return-value]
