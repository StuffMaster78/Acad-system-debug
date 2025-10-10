import os
import logging

celery_app = None

# Only wire Celery when enabled (default on in prod; off in dev if you want)
if os.getenv("ENABLE_CELERY", "1") == "1":
    try:
        from .celery import app as celery_app  # noqa: F401
    except Exception as exc:
        logging.getLogger(__name__).warning("Celery unavailable: %s", exc)

__all__ = ("celery_app",)