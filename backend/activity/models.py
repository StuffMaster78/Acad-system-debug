from __future__ import annotations

import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from activity.constants import ActivityActorType
from activity.constants import ActivityAudience
from activity.constants import ActivitySeverity
from activity.constants import ActivityVerb


class ActivityEvent(models.Model):
    """
    Stores a structured platform activity event.

    Activity events power user feeds, object timelines, dashboards, and
    realtime product visibility. They are not the authoritative audit trail
    for privileged, financial, or sensitive access events.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="activity_events",
    )
    verb = models.CharField(
        max_length=80,
        choices=ActivityVerb.choices,
        db_index=True,
    )
    actor_type = models.CharField(
        max_length=24,
        choices=ActivityActorType.choices,
        default=ActivityActorType.SYSTEM,
    )
    actor_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_actor_events",
    )
    actor_object_id = models.CharField(
        max_length=64,
        blank=True,
    )
    actor = GenericForeignKey(
        "actor_content_type",
        "actor_object_id",
    )
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="activity_target_events",
    )
    target_object_id = models.CharField(
        max_length=64,
        db_index=True,
    )
    target = GenericForeignKey(
        "target_content_type",
        "target_object_id",
    )
    subject_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_subject_events",
    )
    subject_object_id = models.CharField(
        max_length=64,
        blank=True,
    )
    subject = GenericForeignKey(
        "subject_content_type",
        "subject_object_id",
    )
    severity = models.CharField(
        max_length=24,
        choices=ActivitySeverity.choices,
        default=ActivitySeverity.INFO,
        db_index=True,
    )
    audiences = models.JSONField(
        default=list,
        help_text=_("Audience codes allowed to view this event."),
    )
    title = models.CharField(
        max_length=160,
        blank=True,
    )
    summary = models.TextField(
        blank=True,
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
    )
    request_id = models.CharField(
        max_length=64,
        blank=True,
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )
    user_agent = models.TextField(
        blank=True,
    )
    occurred_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-occurred_at", "-created_at"]
        indexes = [
            models.Index(fields=["website", "occurred_at"]),
            models.Index(fields=["website", "verb", "occurred_at"]),
            models.Index(fields=["target_content_type", "target_object_id"]),
            models.Index(fields=["actor_content_type", "actor_object_id"]),
            models.Index(fields=["severity", "occurred_at"]),
        ]
        verbose_name = _("Activity Event")
        verbose_name_plural = _("Activity Events")

    def __str__(self) -> str:
        """
        Return a compact admin representation of the activity event.
        """
        return f"{self.verb} on {self.target_content_type.pk}:{self.target_object_id}"


class ActivityFeedState(models.Model):
    """
    Tracks per user state for an activity event.

    This enables unread counts, dismissals, and pinned feed entries without
    mutating the canonical activity event.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    event = models.ForeignKey(
        ActivityEvent,
        on_delete=models.CASCADE,
        related_name="feed_states",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activity_feed_states",
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,
    )
    is_dismissed = models.BooleanField(
        default=False,
        db_index=True,
    )
    is_pinned = models.BooleanField(
        default=False,
        db_index=True,
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    dismissed_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "user"],
                name="unique_activity_feed_state_per_user",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "is_read", "created_at"]),
            models.Index(fields=["user", "is_dismissed", "created_at"]),
        ]
        verbose_name = _("Activity Feed State")
        verbose_name_plural = _("Activity Feed States")

    def mark_read(self) -> None:
        """
        Mark the feed state as read.
        """
        if self.is_read:
            return

        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=["is_read", "read_at"])

    def dismiss(self) -> None:
        """
        Dismiss the feed state for the user.
        """
        if self.is_dismissed:
            return

        self.is_dismissed = True
        self.dismissed_at = timezone.now()
        self.save(update_fields=["is_dismissed", "dismissed_at"])
