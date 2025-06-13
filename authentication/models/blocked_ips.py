from django.db import models
from django.utils.timezone import now


class BlockedIP(models.Model):
    """
    Stores blocked IPs per website for excessive failed login attempts.
    """
    website = models.ForeignKey(
        "websites.Website", on_delete=models.CASCADE,
        related_name="blocked_ips"
    )
    ip_address = models.GenericIPAddressField()
    blocked_until = models.DateTimeField(
        help_text="Time until this IP is blocked."
    )

    class Meta:
        unique_together = ("website", "ip_address")

    def is_blocked(self):
        """Checks if the IP is still blocked."""
        return self.blocked_until > now()
    

class BlockedIPLog(models.Model):
    """
    Stores the logs of the blocked ips per website.
    """
    ip_address = models.GenericIPAddressField()
    website = models.ForeignKey(
        'websites.Website', on_delete=models.CASCADE,
        related_name='blocked_ip_logs'
    )
    reason = models.TextField()
    blocked_at = models.DateTimeField(auto_now_add=True)
    duration_minutes = models.IntegerField()