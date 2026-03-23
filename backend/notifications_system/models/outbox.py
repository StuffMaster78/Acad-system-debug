from django.conf import settings
from django.db import models
from django.utils import timezone
from notifications_system.enums import DeliveryStatus


class Outbox(models.Model):
    """
    Outbox pattern — events written in the same transaction as the
    domain mutation that triggered them.

    A background worker polls unprocessed rows and dispatches
    notifications, ensuring no event is lost even if the worker
    is down when the mutation occurs.

    Flow:
        1. Domain service writes Outbox row inside its transaction
        2. Worker picks up rows where processed_at IS NULL
        3. Worker dispatches to NotificationService
        4. Worker marks row as processed or failed
    """
    PENDING = 'pending'
    PROCESSING = 'processing'
    PROCESSED = 'processed'
    FAILED = 'failed'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (PROCESSED, 'Processed'),
        (FAILED, 'Failed — max retries exceeded'),
    ]

    event_key = models.CharField(max_length=128)

    website = models.ForeignKey(
        'websites.Website',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='outbox_events',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='outbox_events',
    )

    payload = models.JSONField(default=dict, blank=True)

    # Prevents duplicate events from being processed twice
    dedupe_key = models.CharField(
        max_length=256,
        blank=True,
        unique=True,
        help_text="Unique key to prevent duplicate event processing.",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
        db_index=True,
    )

    attempts = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    last_error = models.TextField(blank=True)
    next_retry_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the worker should next attempt this event.",
    )

    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notif_outbox'
        indexes = [
            # Primary worker query — unprocessed pending items
            models.Index(fields=['status', 'next_retry_at']),
            models.Index(fields=['event_key']),
            models.Index(fields=['processed_at']),
        ]

    def __str__(self):
        return f"{self.event_key} [{self.status}] attempts={self.attempts}"

    @property
    def is_processable(self):
        """True if this event is ready to be picked up by the worker."""
        if self.status not in (self.PENDING, self.PROCESSING):
            return False
        if self.next_retry_at and self.next_retry_at > timezone.now():
            return False
        return True

    @property
    def has_retries_remaining(self):
        return self.attempts < self.max_retries

    def mark_processed(self):
        """Mark event as successfully processed."""
        self.status = self.PROCESSED
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at'])

    def mark_failed(self, error=''):
        """
        Record a failed attempt.
        Schedules retry with exponential backoff or marks as permanently failed.
        """
        self.attempts += 1
        self.last_error = error

        if self.has_retries_remaining:
            self.status = self.PROCESSING
            backoff_minutes = 2 ** self.attempts
            self.next_retry_at = timezone.now() + timezone.timedelta(
                minutes=backoff_minutes
            )
        else:
            self.status = self.FAILED
            self.next_retry_at = None

        self.save(update_fields=[
            'attempts', 'last_error', 'status', 'next_retry_at'
        ])