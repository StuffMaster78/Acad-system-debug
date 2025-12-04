from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from websites.models import Website


class ContentEvent(models.Model):
    """
    Generic content engagement event (views, scroll, clicks, likes, etc.).
    Designed as an append-only log that can be aggregated into dashboards.
    """

    class EventType(models.TextChoices):
        VIEW = "view", "View"
        SCROLL = "scroll_depth", "Scroll depth"
        CLICK = "click", "Click"
        CTA = "cta", "Call-to-action"
        LIKE = "like", "Like"
        DISLIKE = "dislike", "Dislike"

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="content_events",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="content_events",
    )
    session_id = models.CharField(
        max_length=64,
        blank=True,
        help_text="Anonymous session identifier for approximate uniques.",
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Arbitrary JSON metadata (e.g. scroll_percent, element_id).",
    )

    path = models.CharField(max_length=512, blank=True)
    referrer = models.CharField(max_length=512, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["website", "event_type", "created_at"]),
            models.Index(fields=["website", "content_type", "object_id"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.website} {self.event_type} for {self.content_type_id}:{self.object_id}"


