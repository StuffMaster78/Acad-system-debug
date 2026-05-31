"""
CMS Intelligence
==================

The operational brain. Six subsystems:
1. GSC daily metrics (ingested nightly from Google Search Console)
2. GA4 daily metrics (ingested nightly from Google Analytics 4)
3. Content performance snapshots (materialized nightly)
4. Freshness alerts (six-criteria scanner)
5. Conversion attribution (four models per order)
6. Content embeddings (for similarity-based linking)

All data is per-tenant (site FK) and resolved to content pages.
"""

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


# ===========================================================================
# 1. GSC Daily Metrics
# ===========================================================================

class GSCDailyMetric(models.Model):
    """One row per (site, date, page_path, query) tuple.
    Pulled nightly via Google Search Console API."""

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="gsc_metrics",
    )
    date = models.DateField(db_index=True)

    page_path = models.CharField(max_length=500, db_index=True)
    query = models.CharField(max_length=500)

    # Metrics
    clicks = models.PositiveIntegerField(default=0)
    impressions = models.PositiveIntegerField(default=0)
    ctr = models.FloatField(default=0.0)
    position = models.FloatField(default=0.0)

    # AI Overview appearance (Search Console added this mid-2025)
    appeared_in_ai_overview = models.BooleanField(default=False)

    # Resolved content page (set during ingestion)
    resolved_page_content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True,
    )
    resolved_page_object_id = models.PositiveIntegerField(null=True, blank=True)
    resolved_page = GenericForeignKey(
        "resolved_page_content_type", "resolved_page_object_id",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["site", "date", "page_path", "query"]
        indexes = [
            models.Index(fields=["site", "date"]),
            models.Index(fields=["site", "page_path", "date"]),
            models.Index(fields=["resolved_page_content_type", "resolved_page_object_id", "date"]),
        ]


# ===========================================================================
# 2. GA4 Daily Metrics
# ===========================================================================

class GA4DailyMetric(models.Model):
    """One row per (site, date, page_path, channel) tuple.
    Pulled nightly via GA4 Data API."""

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="ga4_metrics",
    )
    date = models.DateField(db_index=True)

    page_path = models.CharField(max_length=500, db_index=True)
    channel = models.CharField(
        max_length=100,
        db_index=True,
        help_text="sessionDefaultChannelGroup: organic, direct, referral, social, paid",
    )

    # Metrics
    page_views = models.PositiveIntegerField(default=0)
    sessions = models.PositiveIntegerField(default=0)
    engaged_sessions = models.PositiveIntegerField(default=0)
    avg_engagement_seconds = models.FloatField(default=0.0)
    conversions = models.PositiveIntegerField(default=0)

    # Resolved content page
    resolved_page_content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True,
    )
    resolved_page_object_id = models.PositiveIntegerField(null=True, blank=True)
    resolved_page = GenericForeignKey(
        "resolved_page_content_type", "resolved_page_object_id",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["site", "date", "page_path", "channel"]
        indexes = [
            models.Index(fields=["site", "date"]),
            models.Index(fields=["site", "page_path", "date"]),
        ]


# ===========================================================================
# 3. Content Performance Snapshot
# ===========================================================================

class ContentPerformanceSnapshot(models.Model):
    """Pre-computed performance metrics per content page. Refreshed nightly.

    This is what the dashboard queries — fast reads, no aggregation at request time.
    """

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="performance_snapshots",
    )

    # The content page
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    page_title = models.CharField(max_length=255, blank=True)
    page_slug = models.CharField(max_length=255, blank=True)

    # --- Trailing 30 days ---
    gsc_clicks_30d = models.PositiveIntegerField(default=0)
    gsc_impressions_30d = models.PositiveIntegerField(default=0)
    gsc_avg_position_30d = models.FloatField(default=0.0)
    gsc_avg_ctr_30d = models.FloatField(default=0.0)

    ga4_page_views_30d = models.PositiveIntegerField(default=0)
    ga4_sessions_30d = models.PositiveIntegerField(default=0)
    ga4_avg_engagement_30d = models.FloatField(default=0.0)

    internal_conversions_30d = models.PositiveIntegerField(default=0)
    attributed_revenue_30d = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )

    # --- Trailing 90 days ---
    gsc_clicks_90d = models.PositiveIntegerField(default=0)
    ga4_page_views_90d = models.PositiveIntegerField(default=0)

    # --- Deltas (vs previous 30-day period) ---
    clicks_delta_pct = models.FloatField(
        default=0.0,
        help_text="Percentage change in clicks vs previous 30 days",
    )
    position_delta = models.FloatField(
        default=0.0,
        help_text="Change in avg position (positive = worsened)",
    )

    # --- AI Overview ---
    ai_overview_appearances_30d = models.PositiveIntegerField(default=0)

    # --- Diagnosis ---
    DIAGNOSIS_CHOICES = [
        ("healthy", "Healthy"),
        ("low_ctr", "High impressions, low CTR — rewrite title/meta"),
        ("low_engagement", "High CTR, low engagement — page over-promised"),
        ("no_conversion_path", "Traffic but no conversions — add CTAs"),
        ("declining_position", "Position declining — refresh content"),
        ("not_visible", "No impressions — check indexation"),
    ]
    diagnosis = models.CharField(
        max_length=30,
        choices=DIAGNOSIS_CHOICES,
        default="healthy",
    )

    last_computed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["content_type", "object_id"]
        indexes = [
            models.Index(fields=["site", "gsc_clicks_30d"]),
            models.Index(fields=["site", "internal_conversions_30d"]),
            models.Index(fields=["site", "attributed_revenue_30d"]),
            models.Index(fields=["site", "diagnosis"]),
        ]


# ===========================================================================
# 4. Freshness Alerts
# ===========================================================================

class FreshnessAlert(models.Model):
    """A freshness signal on a content page.
    Raised by the nightly scanner when any of six criteria are met."""

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="freshness_alerts",
    )

    # The page
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    ALERT_TYPE_CHOICES = [
        ("age_threshold", "Age threshold exceeded"),
        ("position_decline", "Search position declined"),
        ("click_decline", "Click traffic declined"),
        ("engagement_decline", "Engagement declined"),
        ("editor_flagged", "Manually flagged by editor"),
        ("topic_event", "External topic event"),
    ]
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)

    severity = models.PositiveSmallIntegerField(
        default=3,
        help_text="1 (low) to 5 (critical). Severity 3+ triggers notifications.",
    )

    # Data backing the alert
    detail = models.JSONField(
        default=dict,
        help_text=(
            "Numbers backing the alert, e.g., "
            '{"old_position": 4.2, "new_position": 11.8, "delta": 7.6}'
        ),
    )

    # Lifecycle
    raised_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acknowledged_alerts",
    )

    RESOLUTION_CHOICES = [
        ("", "Unresolved"),
        ("updated", "Content updated"),
        ("dismissed", "Dismissed as not actionable"),
        ("archived", "Content archived"),
        ("rewritten", "Rewritten from scratch"),
        ("auto_resolved", "Condition resolved itself"),
    ]
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution = models.CharField(
        max_length=20,
        choices=RESOLUTION_CHOICES,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["site", "resolved_at"]),
            models.Index(fields=["content_type", "object_id", "resolved_at"]),
            models.Index(fields=["severity", "resolved_at"]),
        ]
        ordering = ["-severity", "-raised_at"]


# ===========================================================================
# 5. Conversion Attribution
# ===========================================================================

class ConversionAttribution(models.Model):
    """Per (order, content_page, attribution_model) — how much credit
    does this content page get for this order?

    Four models computed per conversion:
    - first_touch: first page in the visitor's session
    - last_touch: last page before the order form
    - linear: even credit across all pages
    - position_based: 40% first, 40% last, 20% middle
    """

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="content_attributions",
    )

    # The content page
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    ATTRIBUTION_MODEL_CHOICES = [
        ("first_touch", "First touch"),
        ("last_touch", "Last touch"),
        ("linear", "Linear"),
        ("position_based", "Position-based (40/40/20)"),
    ]
    attribution_model = models.CharField(
        max_length=20,
        choices=ATTRIBUTION_MODEL_CHOICES,
    )

    # Credit
    credit_share = models.FloatField(
        help_text="0.0 to 1.0 — fraction of credit assigned",
    )
    attributed_revenue = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    # Path position
    path_position = models.PositiveSmallIntegerField(
        help_text="1 = first page visited, n = last before conversion",
    )
    path_length = models.PositiveSmallIntegerField(
        help_text="Total pages in the conversion path",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["order", "content_type", "object_id", "attribution_model"]
        indexes = [
            models.Index(fields=["content_type", "object_id", "attribution_model"]),
        ]


# ===========================================================================
# 6. Content Embeddings
# ===========================================================================

class ContentEmbedding(models.Model):
    """Vector embedding per content page.
    Generated on publish via OpenAI text-embedding-3-small (or equivalent).
    Used by cms_content_graph's InternalLinkingService for similarity matching.
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    # The embedding vector (1536 dimensions for text-embedding-3-small)
    embedding = models.JSONField(
        help_text="Vector as a list of floats",
    )
    model_name = models.CharField(
        max_length=100,
        default="text-embedding-3-small",
    )

    # Text that was embedded (for debugging and re-generation)
    source_text_hash = models.CharField(
        max_length=64,
        help_text="SHA-256 of the text that produced this embedding",
    )

    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["content_type", "object_id"]


# ===========================================================================
# 7. Task Sync Log — persistent record of scheduled intelligence task runs
# ===========================================================================

class TaskSyncLog(models.Model):
    """
    Written by each Celery intelligence task at completion.
    Gives staff a persistent, per-site view of when data was last ingested
    and whether it succeeded — independent of Redis result-backend lifetime.
    """

    TASK_CHOICES = [
        ("gsc", "GSC ingestion"),
        ("ga4", "GA4 ingestion"),
        ("freshness", "Freshness scanner"),
        ("snapshot", "Performance snapshots"),
        ("attribution", "Conversion attribution"),
        ("embeddings", "Embedding generation"),
    ]

    STATUS_CHOICES = [
        ("success", "Success"),
        ("partial", "Partial — some sites failed"),
        ("failed", "Failed"),
        ("skipped", "Skipped — no config"),
    ]

    task = models.CharField(max_length=30, choices=TASK_CHOICES, db_index=True)
    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="sync_logs",
        null=True, blank=True,
        help_text="Null = platform-wide task (e.g. embeddings)",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="success")
    rows_processed = models.PositiveIntegerField(default=0)
    duration_seconds = models.FloatField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    ran_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-ran_at"]
        indexes = [
            models.Index(fields=["task", "-ran_at"]),
            models.Index(fields=["site", "task", "-ran_at"]),
        ]

    def __str__(self) -> str:
        site_name = self.site.site_name if self.site_id else "all sites"
        return f"{self.task} | {site_name} | {self.status} @ {self.ran_at:%Y-%m-%d %H:%M}"