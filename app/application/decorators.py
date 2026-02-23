from functools import wraps

from app.core.context import get_session


def transactional(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        session = get_session()
        try:
            result = fn(*args, **kwargs)
            session.commit()
            return result
        except Exception:
            session.rollback()
            raise

    return wrapper
