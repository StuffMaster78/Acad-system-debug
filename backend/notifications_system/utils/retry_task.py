"""Utility for retrying tasks with exponential backoff."""

import logging
import time
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


def retry_task_with_backoff(
    task: Callable[[], Any],
    max_retries: int = 3,
    base_backoff: int = 5,
    raise_on_fail: bool = False,
) -> Optional[Any]:
    """Run a task with retries using exponential backoff.

    Args:
        task: Callable with no arguments to execute.
        max_retries: Number of attempts before giving up.
        base_backoff: Initial sleep time in seconds. Doubled each retry.
        raise_on_fail: If True, re-raises the last exception.

    Returns:
        The result of `task()` if it succeeds, or None if it fails and
        `raise_on_fail` is False.
    """
    for attempt in range(max_retries):
        try:
            return task()
        except Exception as exc:  # noqa: BLE001
            wait = base_backoff * (2**attempt)
            logger.warning(
                "Task failed on attempt %s/%s: %s. Retrying in %s sec...",
                attempt + 1,
                max_retries,
                exc,
                wait,
            )
            time.sleep(wait)

    logger.error("Task failed after %s retries", max_retries)
    if raise_on_fail:
        raise
    return None