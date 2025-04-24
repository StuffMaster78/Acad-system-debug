from django.db import models
from django.utils.timezone import now


class BlockedIP(models.Model):
    """
    Stores blocked IPs for excessive failed login attempts.
    """
    ip_address = models.GenericIPAddressField(unique=True)
    blocked_until = models.DateTimeField(
        help_text="Time until this IP is blocked."
    )

    def is_blocked(self):
        """Checks if the IP is still blocked."""
        return self.blocked_until > now()