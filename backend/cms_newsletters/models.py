"""
CMS Newsletters
=================

Direct audience channel. The lifeline when organic search declines.

Subscribers come from:
- Email-gated attachment downloads (cms_attachments.EmailGatedAccess)
- Blog signup forms
- Order completion opt-ins
- Manual import

Newsletters use StreamField blocks (reused from cms_core) for rich content.
Automation sequences trigger email flows (download → welcome → tip → offer).
"""

from django.conf import settings
from django.db import models

from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

from cms_core.blocks import BLOG_BLOCKS


class SubscriberCategory(models.Model):
    """Topic preferences for subscribers (e.g., 'Nursing Tips', 'Essay Guides')."""

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="subscriber_categories",
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ["site", "slug"]
        ordering = ["name"]
        verbose_name_plural = "Subscriber Categories"

    def __str__(self):
        return self.name


class Subscriber(models.Model):
    """An email subscriber. Tenant-scoped."""

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="subscribers",
    )
    email = models.EmailField()
    is_active = models.BooleanField(default=True)

    # Subscription preferences
    FREQUENCY_CHOICES = [
        ("weekly", "Weekly digest"),
        ("monthly", "Monthly digest"),
        ("instant", "Every new post"),
    ]
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default="weekly",
    )
    categories = models.ManyToManyField(
        SubscriberCategory,
        blank=True,
        related_name="subscribers",
    )

    # Consent (GDPR compliance)
    consent_marketing = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)

    # Source attribution — where did this subscriber come from?
    SOURCE_CHOICES = [
        ("attachment_gate", "Email-gated attachment download"),
        ("blog_form", "Blog signup form"),
        ("order_optin", "Order completion opt-in"),
        ("manual", "Manual / admin import"),
        ("import", "Bulk import"),
    ]
    source = models.CharField(
        max_length=30,
        choices=SOURCE_CHOICES,
        default="blog_form",
    )
    source_detail = models.CharField(
        max_length=255,
        blank=True,
        help_text="Which attachment, blog post, or import batch led to this signup",
    )

    # Engagement tracking
    open_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)
    last_opened_at = models.DateTimeField(null=True, blank=True)
    last_clicked_at = models.DateTimeField(null=True, blank=True)

    # Unsubscribe
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    UNSUBSCRIBE_REASON_CHOICES = [
        ("too_frequent", "Too frequent"),
        ("not_relevant", "Not relevant"),
        ("never_subscribed", "Never subscribed"),
        ("other", "Other"),
    ]
    unsubscribe_reason = models.CharField(
        max_length=30,
        choices=UNSUBSCRIBE_REASON_CHOICES,
        blank=True,
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["site", "email"]
        indexes = [
            models.Index(fields=["site", "is_active"]),
            models.Index(fields=["site", "source"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.email} ({self.site.site_name})"


class Newsletter(models.Model):
    """A single newsletter issue. Uses StreamField for rich content."""

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="newsletters",
    )

    title = models.CharField(max_length=255, help_text="Internal title")
    subject_line = models.CharField(max_length=200)
    preview_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Preview text shown in email clients",
    )

    # Content — reuses blog blocks for rich formatting
    body = StreamField(BLOG_BLOCKS, use_json_field=True, blank=True)

    # Targeting
    category = models.ForeignKey(
        SubscriberCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Only send to subscribers of this category (blank = all)",
    )

    # Sender
    sender_name = models.CharField(max_length=100, blank=True)
    sender_email = models.EmailField(blank=True)

    # A/B subject testing
    subject_line_b = models.CharField(
        max_length=200,
        blank=True,
        help_text="Variant B subject line for A/B testing (blank = no test)",
    )
    ab_split_percentage = models.PositiveSmallIntegerField(
        default=50,
        help_text="Percentage of recipients who get variant B",
    )

    # Status
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
        ("sending", "Sending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )
    scheduled_send_date = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("site"),
        MultiFieldPanel([
            FieldPanel("title"),
            FieldPanel("subject_line"),
            FieldPanel("preview_text"),
            FieldPanel("subject_line_b"),
            FieldPanel("ab_split_percentage"),
        ], heading="Subject & Preview"),
        MultiFieldPanel([
            FieldPanel("sender_name"),
            FieldPanel("sender_email"),
            FieldPanel("category"),
        ], heading="Targeting"),
        FieldPanel("body"),
        MultiFieldPanel([
            FieldPanel("status"),
            FieldPanel("scheduled_send_date"),
        ], heading="Scheduling"),
    ]

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.status})"


class NewsletterEvent(models.Model):
    """Per-subscriber-per-newsletter tracking event."""

    newsletter = models.ForeignKey(
        Newsletter,
        on_delete=models.CASCADE,
        related_name="events",
    )
    subscriber = models.ForeignKey(
        Subscriber,
        on_delete=models.CASCADE,
        related_name="newsletter_events",
    )

    EVENT_TYPE_CHOICES = [
        ("delivered", "Delivered"),
        ("opened", "Opened"),
        ("clicked", "Clicked"),
        ("bounced", "Bounced"),
        ("complained", "Complained (spam)"),
        ("unsubscribed", "Unsubscribed"),
    ]
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)

    # For click events — which link was clicked
    link_url = models.URLField(blank=True)

    # Which subject variant they received (for A/B analysis)
    subject_variant = models.CharField(
        max_length=1,
        choices=[("A", "A"), ("B", "B")],
        default="A",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["newsletter", "event_type"]),
            models.Index(fields=["subscriber", "created_at"]),
        ]


class NewsletterAnalytics(models.Model):
    """Materialized per-newsletter summary. Computed after send completes."""

    newsletter = models.OneToOneField(
        Newsletter,
        on_delete=models.CASCADE,
        related_name="analytics",
    )

    sent_count = models.PositiveIntegerField(default=0)
    delivered_count = models.PositiveIntegerField(default=0)
    open_count = models.PositiveIntegerField(default=0)
    open_rate = models.FloatField(default=0.0)
    click_count = models.PositiveIntegerField(default=0)
    click_rate = models.FloatField(default=0.0)
    bounce_count = models.PositiveIntegerField(default=0)
    bounce_rate = models.FloatField(default=0.0)
    complaint_count = models.PositiveIntegerField(default=0)
    unsubscribe_count = models.PositiveIntegerField(default=0)

    # A/B results
    subject_a_open_rate = models.FloatField(default=0.0)
    subject_b_open_rate = models.FloatField(default=0.0)
    winning_subject = models.CharField(max_length=1, blank=True)

    # Conversion attribution
    conversion_count = models.PositiveIntegerField(default=0)
    conversion_revenue = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
    )

    computed_at = models.DateTimeField(auto_now=True)


# ===========================================================================
# AUTOMATION SEQUENCES
# ===========================================================================

class AutomationSequence(models.Model):
    """A triggered email sequence (e.g., attachment download → follow-up flow).

    Steps fire on a schedule after the trigger event.
    """

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="automation_sequences",
    )
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    TRIGGER_TYPE_CHOICES = [
        ("attachment_download", "Attachment download (email-gated)"),
        ("new_subscriber", "New subscriber signup"),
        ("order_complete", "Order completed"),
        ("inactivity", "Subscriber inactivity (no opens in 90 days)"),
    ]
    trigger_type = models.CharField(
        max_length=30,
        choices=TRIGGER_TYPE_CHOICES,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.trigger_type})"


class AutomationStep(models.Model):
    """A single email in an automation sequence."""

    sequence = models.ForeignKey(
        AutomationSequence,
        on_delete=models.CASCADE,
        related_name="steps",
    )
    step_order = models.PositiveSmallIntegerField()
    delay_days = models.PositiveSmallIntegerField(
        help_text="Days after trigger (or previous step) to send this email",
    )

    subject_line = models.CharField(max_length=200)
    body = StreamField(BLOG_BLOCKS, use_json_field=True, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sequence", "step_order"]
        unique_together = ["sequence", "step_order"]

    def __str__(self):
        return f"{self.sequence.name} — Step {self.step_order}"


class AutomationEnrollment(models.Model):
    """Tracks which subscriber is in which sequence and their progress."""

    subscriber = models.ForeignKey(
        Subscriber,
        on_delete=models.CASCADE,
        related_name="automation_enrollments",
    )
    sequence = models.ForeignKey(
        AutomationSequence,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )

    # Progress
    current_step = models.PositiveSmallIntegerField(default=0)
    next_send_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the next email in the sequence fires",
    )

    # Status
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("paused", "Paused"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )

    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["subscriber", "sequence"]
        indexes = [
            models.Index(fields=["status", "next_send_at"]),
        ]

    def __str__(self):
        return f"{self.subscriber.email} in {self.sequence.name} (step {self.current_step})"