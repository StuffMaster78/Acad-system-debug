from django.db import models
# from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid

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
        related_name="audit_logs",
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

    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Time the audit log entry was recorded.")
    )

    class Meta:
        verbose_name = _("Audit Log Entry")
        verbose_name_plural = _("Audit Log Entries")
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=['actor', 'target', 'target_id']),
        ]

    def __str__(self):
        actor = self.actor.username if self.actor else "System"
        return f"[{self.timestamp}] {actor} - {self.action} {self.target} ({self.target_id})"