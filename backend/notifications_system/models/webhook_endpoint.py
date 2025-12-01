from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import F
from django.utils import timezone

from notifications_system.enums import NotificationChannel


class NotificationWebhookEndpoint(models.Model):
    """
    Generic webhook endpoint a user can register to receive notification events.
    Works for any role (client, writer, admin, etc.) and any website/tenant.
    """

    HMAC_ALGOS = (
        ("sha256", "SHA256"),
        ("sha1", "SHA1"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_webhooks",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="notification_webhooks",
    )
    name = models.CharField(max_length=80)
    url = models.URLField(help_text="Destination URL that will receive webhook payloads.")
    secret_token = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional secret used to sign outgoing payloads.",
    )
    signature_algorithm = models.CharField(
        max_length=10,
        choices=HMAC_ALGOS,
        default="sha256",
    )
    include_rendered_fields = models.BooleanField(
        default=True,
        help_text="Include rendered title/message in payload body.",
    )
    headers = models.JSONField(
        default=dict,
        blank=True,
        help_text="Extra HTTP headers to send with webhook requests.",
    )
    timeout_seconds = models.PositiveIntegerField(
        default=5,
        help_text="Request timeout per webhook call.",
    )
    enabled = models.BooleanField(default=True)
    subscribed_events = ArrayField(
        models.CharField(max_length=150),
        blank=True,
        default=list,
        help_text="List of notification event keys this endpoint subscribes to. Empty = all.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_failure_at = models.DateTimeField(null=True, blank=True)
    failure_count = models.PositiveIntegerField(default=0)
    channel = models.CharField(
        max_length=20,
        choices=NotificationChannel.choices,
        default=NotificationChannel.WEBHOOK,
        help_text="Logical channel represented by this endpoint.",
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "website", "name")
        verbose_name = "Notification Webhook Endpoint"
        verbose_name_plural = "Notification Webhook Endpoints"

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.user} · {self.name}"

    @property
    def accepts_all_events(self) -> bool:
        return not self.subscribed_events

    def should_handle(self, event_key: str) -> bool:
        if not event_key:
            return False
        return self.accepts_all_events or event_key in self.subscribed_events

    def mark_success(self) -> None:
        self.last_success_at = timezone.now()
        self.failure_count = 0
        self.save(update_fields=["last_success_at", "failure_count"])

    def mark_failure(self) -> None:
        self.last_failure_at = timezone.now()
        NotificationWebhookEndpoint.objects.filter(pk=self.pk).update(
            last_failure_at=self.last_failure_at,
            failure_count=F("failure_count") + 1,
        )
        # Refresh in-memory value
        self.failure_count += 1

