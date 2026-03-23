# notifications_system/tasks/digest.py
"""Celery beat task for processing due digests."""
from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def process_due_digests() -> None:
    """
    Send all due unsent digests.
    Scheduled via Celery beat — run every hour.
    """
    from notifications_system.services.digest_service import DigestService

    logger.info("process_due_digests: starting.")
    DigestService.send_due_digests()
    logger.info("process_due_digests: complete.")