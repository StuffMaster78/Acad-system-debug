"""
Utility used by all intelligence tasks to write a TaskSyncLog entry.
Call at the end of each task regardless of success or failure.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def log_sync(
    task: str,
    site=None,
    status: str = "success",
    rows_processed: int = 0,
    duration_seconds: float | None = None,
    error_message: str = "",
) -> None:
    """Persist a TaskSyncLog row. Swallows its own exceptions so it never
    breaks the task that called it."""
    try:
        from cms_intelligence.models import TaskSyncLog

        TaskSyncLog.objects.create(
            task=task,
            site=site,
            status=status,
            rows_processed=rows_processed,
            duration_seconds=duration_seconds,
            error_message=error_message or "",
        )
    except Exception as exc:
        logger.warning("sync_logger: could not write TaskSyncLog: %s", exc)
