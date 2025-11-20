from django.conf import settings
from django.db import models
from notifications_system.enums import (
    NotificationChannel, NotificationPriority,
    DeliveryStatus
)
from django.utils import timezone


class Delivery(models.Model):
    """Rows representing sends; drive retries/DLQ/metrics from here."""
    event_key = models.CharField(max_length=128)
    website = models.ForeignKey(
        "websites.Website",
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    channel = models.CharField(
        max_length=16,
        choices=NotificationChannel.choices
    )
    priority = models.CharField(
        max_length=16,
        choices=NotificationPriority.choices
    )
    status = models.CharField(
        max_length=16,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.QUEUED
    )
    attempts = models.PositiveIntegerField(default=0)
    provider = models.CharField(max_length=64, blank=True)
    provider_msg_id = models.CharField(max_length=128, blank=True)
    error_code = models.CharField(max_length=64, blank=True)
    error_detail = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)
    rendered = models.JSONField(default=dict, blank=True)
    dedupe_key = models.CharField(max_length=256, db_index=True, blank=True)
    queued_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "notif_delivery"
        indexes = [
            models.Index(fields=["status", "channel"]),
            models.Index(fields=["user", "website"]),
            models.Index(fields=["event_key"]),
        ]