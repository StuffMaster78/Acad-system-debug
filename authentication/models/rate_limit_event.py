from django.db import models

class RateLimitEvent(models.Model):
    """
    Tracks rate limit events for user actions like login attempts.
    Used to enforce throttling policies based on IP address and website.
    This model is designed to handle multitenancy scenarios where each website
    may have different rate limits.
    """
    user = models.ForeignKey('user.User', null=True, blank=True, on_delete=models.SET_NULL)
    website = models.ForeignKey('websites.Website', on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(null=True, blank=True)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    triggered_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=64, default="login_throttle")

    class Meta:
        indexes = [
            models.Index(fields=["website", "ip_address", "triggered_at"]),
        ]

    def __str__(self):
        return f"[{self.website}] {self.ip_address} ({self.reason})"