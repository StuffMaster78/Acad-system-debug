from contextvars import ContextVar
from typing import Optional

_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)
_website_id: ContextVar[str | None] = ContextVar("website_id", default=None)


class Trace:

    # -------------------------
    # Correlation ID
    # -------------------------

    @staticmethod
    def set_correlation_id(cid: str):
        return _correlation_id.set(cid)

    @staticmethod
    def get_correlation_id() -> str | None:
        return _correlation_id.get()

    @staticmethod
    def reset_correlation_id(token):
        _correlation_id.reset(token)

    # -------------------------
    # Website ID
    # -------------------------

    @staticmethod
    def set_website_id(wid: str):
        return _website_id.set(wid)

    @staticmethod
    def get_website_id() -> str | None:
        return _website_id.get()

    @staticmethod
    def reset_website_id(token):
        _website_id.reset(token)