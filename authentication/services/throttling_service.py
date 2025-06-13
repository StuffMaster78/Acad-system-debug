from django.utils import timezone
from datetime import timedelta
from authentication.models.fingerprinting import DeviceFingerprint


class RiskThrottleService:
    """Throttle login attempts or fingerprint creations per user/tenant."""

    def __init__(self, user, website):
        self.user = user
        self.website = website

    def too_many_risky_devices(self, time_window_minutes=30, limit=5):
        """
        Check if user has registered too many untrusted devices recently.

        Returns:
            bool: True if throttled.
        """
        threshold_time = timezone.now() - timedelta(minutes=time_window_minutes)
        count = DeviceFingerprint.objects.filter(
            user=self.user,
            website=self.website,
            trusted=False,
            created_at__gte=threshold_time
        ).count()
        return count >= limit