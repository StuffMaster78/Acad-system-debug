"""
Public health check endpoints for high availability.

Endpoints:
    GET /health/ — deep check: DB + cache + celery + storage
    GET /health/ready/ — readiness: DB + cache must pass (used by LB)
    GET /health/live/ — liveness: process alive (used by container runtime)
"""
from __future__ import annotations

import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

APP_VERSION = getattr(settings, "APP_VERSION", "unknown")


@require_http_methods(["GET"])
@never_cache
def health_check(request):
    """
    Deep health check — DB, cache, Celery workers, and storage.
    Returns 200 (healthy or degraded) or 503 (critical failure).
    System continues serving even in degraded state.
    """
    t0 = time.time()

    db = _check_database()
    redis = _check_cache()
    celery = _check_celery()
    storage = _check_storage()

    critical_failure = db["status"] == "error"
    degraded = any(
        s["status"] == "error"
        for s in [db, redis, celery, storage]
    )

    status = "healthy"
    if critical_failure:
        status = "critical"
    elif degraded:
        status = "degraded"

    return JsonResponse(
        {
            "status": status,
            "version": APP_VERSION,
            "timestamp": time.time(),
            "duration_ms": round((time.time() - t0) * 1000, 2),
            "services": {
                "database": db,
                "cache": redis,
                "celery": celery,
                "storage": storage,
            },
        },
        status=503 if critical_failure else 200,
    )


@require_http_methods(["GET"])
@never_cache
def health_ready(request):
    """
    Readiness check — 200 only when DB and cache are reachable.
    Used by load balancers and orchestration systems to gate traffic.
    """
    db = _check_database()
    redis = _check_cache()

    ready = db["status"] == "healthy" and redis["status"] == "healthy"

    return JsonResponse(
        {
            "status": "ready" if ready else "not_ready",
            "timestamp": time.time(),
            "checks": {"database": db, "cache": redis},
        },
        status=200 if ready else 503,
    )


@require_http_methods(["GET"])
@never_cache
def health_live(request):
    """
    Liveness check — 200 as long as the process can respond.
    Never returns 503 unless the process is completely dead.
    """
    return JsonResponse(
        {"status": "alive", "version": APP_VERSION, "timestamp": time.time()},
        status=200,
    )


# ------------------------------------------------------------------
# Internal checkers
# ------------------------------------------------------------------

def _check_database() -> dict:
    try:
        t0 = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return {"status": "healthy", "response_time_ms": _ms(t0)}
    except Exception as exc:
        logger.warning("DB health check failed: %s", exc)
        return {"status": "error", "error": "database check failed"}


def _check_cache() -> dict:
    try:
        t0 = time.time()
        key = f"health:{t0}"
        cache.set(key, "ok", timeout=10)
        val = cache.get(key)
        cache.delete(key)
        if val == "ok":
            return {"status": "healthy", "response_time_ms": _ms(t0)}
        return {"status": "error", "error": "cache check failed"}
    except Exception as exc:
        logger.warning("Cache health check failed: %s", exc)
        return {"status": "error", "error": "cache check failed"}


def _check_celery() -> dict:
    """
    Verify Celery workers are reachable by pinging the control channel.
    Uses a short timeout (2 s) so this never blocks the health response.
    """
    try:
        from celery import current_app

        t0 = time.time()
        inspector = current_app.control.inspect(timeout=2.0)
        ping_result = inspector.ping() # dict of {worker: {ok: "pong"}} or None

        if ping_result:
            worker_count = len(ping_result)
            return {
                "status": "healthy",
                "workers": worker_count,
                "response_time_ms": _ms(t0),
            }
        # No workers responded — not necessarily fatal; warn only
        return {
            "status": "warning",
            "workers": 0,
            "note": "No Celery workers responded to ping",
        }
    except Exception as exc:
        logger.warning("Celery health check failed: %s", exc)
        return {"status": "error", "error": str(exc)}


def _check_storage() -> dict:
    """
    Write and delete a tiny probe file to verify the storage backend is writable.
    Uses Django's default storage (local or S3/DO Spaces).
    """
    try:
        from django.core.files.base import ContentFile
        from django.core.files.storage import default_storage

        t0 = time.time()
        probe_path = "health_probes/.probe"
        default_storage.save(probe_path, ContentFile(b"ok"))
        default_storage.delete(probe_path)
        return {"status": "healthy", "response_time_ms": _ms(t0)}
    except Exception as exc:
        logger.warning("Storage health check failed: %s", exc)
        return {"status": "error", "error": str(exc)}


def _ms(t0: float) -> float:
    return round((time.time() - t0) * 1000, 2)
