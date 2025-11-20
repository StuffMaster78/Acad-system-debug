# writing_system/__init__.py
from __future__ import annotations
import os
import logging

log = logging.getLogger(__name__)

# Only wire Celery when explicitly enabled
ENABLE_CELERY = os.getenv("ENABLE_CELERY", "0") == "1"

if ENABLE_CELERY:
    try:
        from .celery import app as celery_app  # real Celery app
        __all__ = ("celery_app",)
    except Exception as exc:  # keep Django booting if Celery is missing/misconfigured
        log.warning("Celery unavailable: %s", exc)
        celery_app = None  # type: ignore
        __all__ = ()
else:
    celery_app = None  # type: ignore
    __all__ = ()