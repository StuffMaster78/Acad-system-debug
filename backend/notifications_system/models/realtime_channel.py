# notifications/models.py

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class RealtimeChannel(models.Model):
    """
    Represents a real-time delivery channel (SSE/WebSocket)
    for a user or group.
    """
    user = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.CASCADE,
        related_name="realtime_channels"
    )
    group = models.CharField(
        max_length=100, blank=True,
        null=True
    )  # e.g. "admins", "writers", "support"
    channel_name = models.CharField(
        max_length=255, unique=True
    )  # e.g. user_32_sse
    is_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.channel_name} ({'user' if self.user else self.group})"
    
    class Meta:
        verbose_name = "Realtime Channel"
        verbose_name_plural = "Realtime Channels"
        ordering = ["-last_seen"]
        indexes = [
            models.Index(fields=["-last_seen"]),
        ]
