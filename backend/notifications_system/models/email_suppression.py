"""
Tracks email addresses that should not receive further email.

Populated by webhook handlers processing provider callbacks
(bounces, spam complaints, unsubscribes).

PreferenceService checks this before dispatching any email delivery.
"""
from __future__ import annotations

from django.db import models
from django.utils import timezone


class SuppressionReason(models.TextChoices):
    BOUNCE_HARD = 'bounce_hard', 'Hard Bounce'
    BOUNCE_SOFT = 'bounce_soft', 'Soft Bounce'
    COMPLAINT = 'complaint', 'Spam Complaint'
    UNSUBSCRIBE = 'unsubscribe', 'Unsubscribe'
    MANUAL = 'manual', 'Manual'


class EmailSuppression(models.Model):
    """
    An email address that must not receive further email from us.

    One row per address — subsequent events for the same address
    update the existing row rather than creating duplicates.
    """
    email = models.EmailField(unique=True, db_index=True)
    reason = models.CharField(
        max_length=20,
        choices=SuppressionReason.choices,
        default=SuppressionReason.BOUNCE_HARD,
    )
    provider = models.CharField(
        max_length=50,
        blank=True,
        help_text="Provider that reported this e.g. 'sendgrid', 'ses'",
    )
    provider_event_id = models.CharField(
        max_length=256,
        blank=True,
        help_text="Provider-side event ID for tracing.",
    )
    raw_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Raw webhook payload for audit.",
    )
    suppressed_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notif_email_suppression'
        verbose_name = 'Email Suppression'
        verbose_name_plural = 'Email Suppressions'

    def __str__(self):
        return f"{self.email} [{self.reason}]"

    @classmethod
    def is_suppressed(cls, email: str) -> bool:
        """Fast check used by PreferenceService before email dispatch."""
        return cls.objects.filter(email__iexact=email).exists()

    @classmethod
    def suppress(
        cls,
        email: str,
        reason: str,
        provider: str = '',
        provider_event_id: str = '',
        raw_payload: dict | None = None,
    ) -> 'EmailSuppression':
        """
        Suppress an address. Updates existing row if present.
        Safe to call multiple times for the same address.
        """
        obj, _ = cls.objects.update_or_create(
            email=email.lower().strip(),
            defaults={
                'reason': reason,
                'provider': provider,
                'provider_event_id': provider_event_id,
                'raw_payload': raw_payload or {},
                'suppressed_at': timezone.now(),
            },
        )
        return obj


class ProviderWebhookEvent(models.Model):
    """
    Raw webhook events received from email providers.

    Written before processing — guarantees the event is not lost
    even if processing fails. A background task processes
    unhandled rows and updates EmailSuppression accordingly.
    """

    PENDING = 'pending'
    PROCESSED = 'processed'
    FAILED = 'failed'
    IGNORED = 'ignored'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSED, 'Processed'),
        (FAILED, 'Failed'),
        (IGNORED, 'Ignored — event type not actionable'),
    ]

    provider = models.CharField(
        max_length=50,
        db_index=True,
        help_text="e.g. 'sendgrid', 'ses', 'mailgun'",
    )
    event_type = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Provider event type e.g. 'bounce', 'complaint', 'delivered'",
    )
    email = models.EmailField(blank=True, db_index=True)
    provider_event_id = models.CharField(max_length=256, blank=True)
    raw_payload = models.JSONField(default=dict)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
        db_index=True,
    )
    error = models.TextField(blank=True)
    received_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notif_provider_webhook_event'
        verbose_name = 'Provider Webhook Event'
        verbose_name_plural = 'Provider Webhook Events'
        indexes = [
            models.Index(fields=['status', 'received_at']),
            models.Index(fields=['provider', 'event_type']),
        ]

    def __str__(self):
        return f"{self.provider} / {self.event_type} / {self.email} [{self.status}]"

    def mark_processed(self):
        self.status = self.PROCESSED
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at'])

    def mark_failed(self, error: str):
        self.status = self.FAILED
        self.error = error
        self.save(update_fields=['status', 'error'])

    def mark_ignored(self):
        self.status = self.IGNORED
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at'])