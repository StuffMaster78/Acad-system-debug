from django.utils import timezone
from datetime import timedelta
from authentication.models.fingerprinting import DeviceFingerprint
from rest_framework.throttling import UserRateThrottle
from authentication.models.rate_limit_event import RateLimitEvent
from authentication.utils.ip import get_client_ip

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
    
class LoginRateThrottle(UserRateThrottle):
    scope = 'login'

    def allow_request(self, request, view):
        """
        Check if the request should be throttled based on user or IP.
        If the user is authenticated, throttle based on user ID.
        If not authenticated, throttle based on IP address.
        """
        self.request = request  # Save for failure
        return super().allow_request(request, view)

    def throttle_failure(self):
        """"Log the rate limit event on throttle failure."""
        request = self.request
        RateLimitEvent.objects.create(
            user=request.user if request.user.is_authenticated else None,
            website=getattr(request, "website", None),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("User-Agent", ""),
            path=request.path,
            method=request.method,
            reason='login_throttle',
        )
        return super().throttle_failure()