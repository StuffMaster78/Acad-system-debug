"""
CMS Engagement
================

Reader interaction signals. No comments — reactions, bookmarks, shares only.

Models use generic FK pattern (content_type + object_id) so they work
with any content type: BlogPostPage, ServicePage, AttachmentLandingPage.

EngagementSummary is a materialized per-page summary refreshed nightly.
"""

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class PageView(models.Model):
    """Individual page view event. Tracked via JS beacon on the public site."""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="page_views",
    )

    # User identification
    session_id = models.CharField(max_length=255, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    referrer = models.URLField(blank=True, max_length=500)
    user_agent = models.TextField(blank=True)

    # Engagement depth (updated via JS beacons during the visit)
    time_on_page = models.PositiveIntegerField(
        default=0,
        help_text="Seconds spent on page",
    )
    scroll_depth = models.PositiveSmallIntegerField(
        default=0,
        help_text="Maximum scroll depth percentage (0-100)",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id", "created_at"]),
            models.Index(fields=["site", "created_at"]),
            models.Index(fields=["session_id"]),
        ]


class PageReaction(models.Model):
    """User reaction to content. One reaction per session per page.
    Toggleable — clicking the same reaction removes it."""

    REACTION_TYPES = [
        ("thumbs_up", "Thumbs Up"),
        ("thumbs_down", "Thumbs Down"),
        ("love", "Love"),
        ("useful", "Found this useful"),
    ]

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="page_reactions",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    session_id = models.CharField(max_length=255, blank=True)

    reaction_type = models.CharField(max_length=20, choices=REACTION_TYPES)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id", "reaction_type"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "object_id", "user"],
                condition=models.Q(user__isnull=False),
                name="unique_reaction_per_user",
            ),
            models.UniqueConstraint(
                fields=["content_type", "object_id", "session_id"],
                condition=models.Q(session_id__gt=""),
                name="unique_reaction_per_session",
            ),
        ]


class PageBookmark(models.Model):
    """Authenticated user saves/bookmarks a page."""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookmarks",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["content_type", "object_id", "user"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]


class PageShare(models.Model):
    """Track share-button clicks on public pages."""

    PLATFORM_CHOICES = [
        ("twitter", "Twitter/X"),
        ("facebook", "Facebook"),
        ("linkedin", "LinkedIn"),
        ("reddit", "Reddit"),
        ("whatsapp", "WhatsApp"),
        ("email", "Email"),
        ("copy_link", "Copy Link"),
    ]

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="page_shares",
    )

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    session_id = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id", "platform"]),
        ]


class EngagementSummary(models.Model):
    """Materialized per-page engagement summary. Refreshed nightly by Celery.

    This is the single source of truth for engagement metrics displayed
    on the admin dashboard and in the public engagement bar.
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="engagement_summaries",
    )

    # View metrics
    total_views = models.PositiveIntegerField(default=0)
    unique_views = models.PositiveIntegerField(default=0)
    avg_time_on_page = models.FloatField(default=0.0)
    avg_scroll_depth = models.FloatField(default=0.0)
    bounce_rate = models.FloatField(
        default=0.0,
        help_text="Percentage of visits with scroll_depth < 25%",
    )

    # Reaction metrics
    thumbs_up_count = models.PositiveIntegerField(default=0)
    thumbs_down_count = models.PositiveIntegerField(default=0)
    love_count = models.PositiveIntegerField(default=0)
    useful_count = models.PositiveIntegerField(default=0)

    # Share metrics
    total_shares = models.PositiveIntegerField(default=0)

    # Computed scores
    engagement_score = models.PositiveIntegerField(
        default=0,
        help_text="Weighted score 0-100 from views, reactions, shares",
    )
    helpfulness_ratio = models.FloatField(
        default=0.0,
        help_text="(positive reactions) / (total reactions), 0.0 to 1.0",
    )

    last_computed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["content_type", "object_id"]
        indexes = [
            models.Index(fields=["site", "engagement_score"]),
            models.Index(fields=["site", "helpfulness_ratio"]),
        ]