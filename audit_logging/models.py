from django.db import models
# from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# User = get_user_model()

class AuditLogEntry(models.Model):
    """
    Stores an audit log entry for critical actions and state changes.
    """

    class Actions(models.TextChoices):
        CREATE = 'CREATE', _('Create')
        UPDATE = 'UPDATE', _('Update')
        DELETE = 'DELETE', _('Delete')
        ACCESS = 'ACCESS', _('Access')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    action = models.CharField(
        max_length=10,
        choices=Actions.choices,
        help_text=_("Short name of the action performed.")
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs_actor",
        help_text=_("The user who performed the action.")
    )

    target = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Target model, e.g., 'orders.Order'.")
    )

    target_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        help_text=_("Primary key of the target object.")
    )

    metadata = models.JSONField(
        blank=True,
        null=True,
        help_text=_("Optional structured metadata about the action.")
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text=_("IP address from which the action was performed.")
    )

    changes = models.JSONField(
        blank=True,
        null=True,
        help_text=_("What changed: {field: {'from': old, 'to': new}}.")
    )

    user_agent = models.CharField(
        max_length=256,
        blank=True,
        help_text=_("User agent string of the actor’s client.")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Time the audit log entry was created.")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Time the audit log entry was last updated.")
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Timestamp of when the action occurred.")
    )
    notes = models.TextField(
        blank=True,
        help_text=_("Optional notes or comments about the action.")
    )
    target_content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    target_object_id = models.PositiveBigIntegerField(
        null=True, blank=True
    )
    target_object = GenericForeignKey(
        'target_content_type', 'target_object_id'
    )
    request_id = models.CharField(
        max_length=64, blank=True, null=True
    )

    class Meta:
        verbose_name = _("Audit Log Entry")
        verbose_name_plural = _("Audit Log Entries")
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=['actor', 'target', 'target_id']),
            models.Index(fields=['action']),
            models.Index(fields=['timestamp']),
        ]

    def get_target_repr(self):
        if self.target_object:
            return str(self.target_object)
        return f"{self.target} ({self.target_id})"


    def __str__(self):
        actor = self.actor.username if self.actor else "System"
        return f"[{self.timestamp}] {actor} - {self.action} {self.get_target_repr()}"

    

class WebhookAuditLog(models.Model):
    """
    Logs all webhook delivery attempts for audit/debugging.
    This model captures details about each webhook event sent, including
    the user, platform, payload, response, and success status.
    Useful for debugging and tracking webhook delivery.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="webhook_user_logs"
    )
    platform = models.CharField(max_length=20)  # slack/discord/custom
    webhook_url = models.URLField()
    event = models.CharField(max_length=50)
    order_id = models.IntegerField(null=True, blank=True)
    payload = models.JSONField()
    response_body = models.TextField(null=True, blank=True)
    response_status = models.IntegerField(null=True, blank=True)
    was_successful = models.BooleanField(default=False)
    is_test = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(auto_now_add=True)
    fallback_icon = models.URLField(null=True, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    target_content_type = models.ForeignKey(
        ContentType, null=True, blank=True,
        on_delete=models.SET_NULL
    )
    target_object_id = models.PositiveBigIntegerField(
        null=True, blank=True
    )
    target_object = GenericForeignKey(
        'target_content_type', 'target_object_id'
    )
    request_id = models.CharField(max_length=64, blank=True, null=True)



    class Meta:
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['event']),
            models.Index(fields=['was_successful']),
        ]
    def __str__(self):
        return f"Webhook {self.event} for {self.platform} at {self.triggered_at} - {'Success' if self.was_successful else 'Failed'}"
    
    def save(self, *args, **kwargs):
        if not self.webhook_url.startswith("http"):
            raise ValueError(
                "Webhook URL must start with 'http' or 'https'"
            )
        super().save(*args, **kwargs)

    def get_payload_summary(self):
        """
        Returns a short summary of the
        payload for display purposes.
        """
        if isinstance(self.payload, dict):
            return {k: v for k, v in self.payload.items() if k in ['id', 'name', 'status']}
        return str(self.payload)[:100]
    
    def get_response_summary(self):
        """
        Returns a short summary of the
        response body for display purposes.
        """
        if self.response_body:
            return self.response_body[:100]
        return "No response body"