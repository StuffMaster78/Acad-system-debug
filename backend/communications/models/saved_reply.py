from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class CommunicationSavedReply(models.Model):
    """
    Reusable tenant scoped reply template for support and admin users.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="communication_saved_replies",
    )

    title = models.CharField(max_length=120)
    body = models.TextField()

    category = models.CharField(max_length=80, blank=True)

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_communication_saved_replies",
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["website", "is_active"]),
            models.Index(fields=["website", "category"]),
            models.Index(fields=["website", "title"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["website", "title"],
                name="unique_communication_saved_reply_title",
            ),
        ]

    def __str__(self) -> str:
        return self.title