import logging
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlmodel import Session
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential, wait_fixed

from app.core.config import settings
from app.core.context import reset_session, set_session

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
)


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(OperationalError),
    before_sleep=lambda retry_state: logger.warning(
        "DB not ready, retrying in %s seconds (attempt %d/5)...",
        retry_state.next_action.sleep,
        retry_state.attempt_number,
    ),
)
def connect_to_db() -> None:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        conn.commit()
    logger.info("Database connection established.")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(0.1),
    retry=retry_if_exception_type(OperationalError),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(
        "Transient DB connection error on request, retrying (attempt %d/3)...",
        retry_state.attempt_number,
    ),
)
def _acquire_session() -> Session:
    """Checkout a DB connection from the pool with retry on transient errors."""
    session = Session(engine)
    session.connection()  # eagerly acquires connection — raises OperationalError if unavailable
    return session


def get_db() -> Generator[Session, None, None]:
    session = _acquire_session()
    token = set_session(session)
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        reset_session(token)
        session.close()
