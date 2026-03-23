# notifications_system/tasks/expiry.py
"""Celery tasks for expiring stale notifications."""
from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def expire_stale_notifications() -> None:
    """
    Mark in-app notifications as expired past their expires_at datetime.
    Scheduled via Celery beat — run every 30 minutes.
    """
    from notifications_system.models.notifications import Notification
    from notifications_system.enums import DeliveryStatus

    count = Notification.objects.filter(
        expires_at__lt=timezone.now(),
        status=DeliveryStatus.SENT,
    ).update(status=DeliveryStatus.CANCELLED)

    if count:
        logger.info("expire_stale_notifications: expired %s notifications.", count)