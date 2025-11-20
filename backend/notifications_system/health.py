# notifications_system/health.py
from __future__ import annotations

import os
import logging
from typing import Dict

from django.db import connection

# Uses your existing implementation in notifications_system/redis_health.py
from .redis_health import check_redis_health

log = logging.getLogger(__name__)

# --- Env flags (dev-friendly defaults) ---
ENABLE_REDIS = os.getenv("ENABLE_REDIS", "0") == "1"
ENABLE_CELERY = os.getenv("ENABLE_CELERY", "1") == "1"
ENV = os.getenv("ENV", "dev")  # "prod" to enforce stricter behavior


def check_db() -> bool:
    """Lightweight DB probe. Returns False on any error."""
    try:
        with connection.cursor() as c:
            c.execute("SELECT 1;")
        return True
    except Exception as exc:
        log.exception("DB health check failed: %s", exc)
        return False


def _check_redis_gate() -> bool:
    """Gate Redis check by flag. True means 'healthy or intentionally disabled'."""
    if not ENABLE_REDIS:
        log.info("Redis disabled in this env; skipping Redis health check.")
        return True
    try:
        # If your check_redis_health() accepts URL, pass it here.
        # Example: check_redis_health(os.getenv("REDIS_URL"))
        return bool(check_redis_health())
    except Exception as exc:
        log.warning("Redis health check failed: %s", exc)
        return False if ENV == "prod" else False  # still False, but we won't raise here


def _check_celery() -> bool:
    """Optional Celery ping. Safe in dev when workers aren't running."""
    if not ENABLE_CELERY:
        log.info("Celery disabled in this env; skipping Celery health check.")
        return True
    try:
        # Try project-local app first; fall back to current_app.
        try:
            from writing_system.celery import app as celery_app  # adjust if your package name differs
        except Exception:
            from celery import current_app as celery_app  # type: ignore

        # app.control.ping() returns a list of dicts from workers; empty if none
        replies = celery_app.control.ping(timeout=1.0)
        ok = bool(replies)
        if not ok:
            log.warning("Celery ping got no replies (workers not running?).")
        return ok
    except Exception as exc:
        log.warning("Celery health check failed: %s", exc)
        return False if ENV == "prod" else False  # still False, but non-fatal here


def healthy() -> Dict[str, bool]:
    """Returns per-subsystem boolean health."""
    return {
        "db": check_db(),
        "redis": _check_redis_gate(),
        "celery": _check_celery(),
    }


def is_healthy() -> bool:
    """Aggregate health. True only if all subsystems report healthy."""
    status = healthy()
    return all(status.values())


def assert_redis_health_or_warn(redis_url: str | None = None) -> None:
    """
    Back-compat helper: use when you want to assert in prod, warn in dev.
    If Redis is disabled by flag, this is a no-op.
    """
    if not ENABLE_REDIS:
        log.info("Redis disabled; assert_redis_health_or_warn no-op.")
        return
    try:
        # Prefer your canonical check (pass URL if your impl supports it).
        _ok = check_redis_health() if redis_url is None else check_redis_health(redis_url)
        if not _ok and ENV == "prod":
            raise RuntimeError("Redis health check failed")
        if not _ok:
            log.warning("Redis unreachable (non-fatal in non-prod).")
    except Exception as exc:
        if ENV == "prod":
            raise
        log.warning("Redis unreachable: %s (non-fatal in %s)", exc, ENV)
