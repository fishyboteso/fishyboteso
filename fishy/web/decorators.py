import logging
import traceback
from functools import wraps

from fishy.web import web


def uses_session(f):
    """directly returns none if it couldn't get session, instead of running the function"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        from .web import get_session
        if get_session(args[0]) is None:
            logging.error("Couldn't create a session")
            return None
        else:
            return f(*args, **kwargs)

    return wrapper


def fallback(default):
    def inner(f):
        # noinspection PyBroadException
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not web.is_online():
                return default

            try:
                return f(*args, **kwargs)
            except Exception:
                traceback.print_exc()
                return default
        return wrapper

    return inner
