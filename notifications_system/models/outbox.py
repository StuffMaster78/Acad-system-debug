from django.conf import settings
from django.db import models
from django.utils import timezone



class Outbox(models.Model):
    """Outbox pattern: write events in the same TX as your domain mutation."""
    event_key = models.CharField(max_length=128)
    website = models.ForeignKey(
        "websites.Website", null=True, blank=True,
        on_delete=models.SET_NULL
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True,
        blank=True, on_delete=models.SET_NULL
    )
    payload = models.JSONField(default=dict, blank=True)
    dedupe_key = models.CharField(max_length=256, blank=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)

    class Meta:
        db_table = "notif_outbox"
        indexes = [
            models.Index(fields=["processed_at"]),
            models.Index(fields=["event_key"]),
        ]
