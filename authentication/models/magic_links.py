import uuid
from django.db import models
from django.utils.timezone import now
from django.conf import settings


class MagicLink(models.Model):
    """
    Stores single-use, expirable magic link tokens for passwordless login.
    """
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="magic_links"
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="magic_links"
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        help_text="Unique magic link token."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text="Expiration time for the magic link."
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Time the magic link was used."
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    user_agent = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        indexes = [
            models.Index(fields=["token", "expires_at"]),
        ]

    def is_valid(self):
        """
        Validates if the token is unused and not expired.
        If expired, logs an audit event and deletes itself.
        """
        if self.used_at is not None:
            return False
        if now() > self.expires_at:
            from authentication.models import AuditLog
            AuditLog.objects.create(
                user=self.user,
                website=self.website,
                event="magic_link_expired",
                ip_address=self.ip_address or "System",
                device=self.user_agent or "Unknown"
            )
            self.delete()
            return False
        return True

    def mark_used(self):
        """
        Marks the token as used and saves the timestamp.
        """
        self.used_at = now()
        self.save(update_fields=["used_at"])

    def __str__(self):
        return f"{self.user.email} | {self.token} | Used: {bool(self.used_at)}"