# writing_system/__init__.py
from __future__ import annotations
import os
import logging

log = logging.getLogger(__name__)

# Import Celery app - this ensures it's available for Celery to discover
# The app is always created, but tasks may not run if ENABLE_CELERY is not set
try:
    from .celery import app as celery_app  # real Celery app
    # Also export as 'app' for Celery's discovery mechanism
    app = celery_app  # noqa: F401
    __all__ = ("celery_app", "app")
except Exception as exc:  # keep Django booting if Celery is missing/misconfigured
    log.warning("Celery unavailable: %s", exc)
    celery_app = None  # type: ignore
    app = None  # type: ignore
    __all__ = ()