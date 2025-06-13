from authentication.models.logout import LogoutEvent
from django.utils import timezone
from datetime import timedelta


class LogoutThrottleService:
    """
    Detects abnormal or excessive logout activity for a user.
    """

    def __init__(self, user, website):
        self.user = user
        self.website = website

    def is_abusing_logout(self, window_minutes=10, max_count=5):
        """
        Returns True if too many logouts in the time window.
        """
        time_window = timezone.now() - timedelta(minutes=window_minutes)
        recent_logouts = LogoutEvent.objects.filter(
            user=self.user,
            timestamp__gte=time_window,
            reason="user_initiated"
        ).count()
        return recent_logouts >= max_count