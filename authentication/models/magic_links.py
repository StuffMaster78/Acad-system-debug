import uuid
from django.db import models
from django.utils.timezone import now
from django.conf import settings
from users.models import User


class MagicLink(models.Model):
    """
    Stores magic link login tokens with expiration.
    """
    user = models.ForeignKey(
        User,
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

    def is_valid(self):
        """Checks if the magic link token is still valid."""
        if self.expires_at < now():
            from users.models import AuditLog
            AuditLog.objects.create(
                user=self.user,
                action="MAGIC_LINK_EXPIRED",
                ip_address="System"
            )
            self.delete()  # Delete expired token
            return False
        return True
