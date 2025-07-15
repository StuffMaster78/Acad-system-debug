from django.utils import timezone
from authentication.models.failed_logins import FailedLoginAttempt
from authentication.services.geo import GeoService

class FailedLoginService:
    """
    Service for tracking failed login attempts and handling lockout logic.
    """

    def __init__(self, user, website):
        """
        Initializes the service with user and website context.

        Args:
            user (User): The user attempting to log in.
            website (Website): The tenant or client site.
        """
        self.user = user
        self.website = website

    def record_failure(self):
        """
        Records a new failed login attempt for the user and website.
        """
        FailedLoginAttempt.objects.create(
            user=self.user,
            website=self.website,
            timestamp=timezone.now()
        )

    def is_locked_out(self, window_minutes=15, max_attempts=5):
        """
        Checks whether the user is locked out based on recent failures.

        Args:
            window_minutes (int): Timeframe to evaluate (in minutes).
            max_attempts (int): Max allowed failures in the timeframe.

        Returns:
            bool: True if locked out, else False.
        """
        time_threshold = timezone.now() - timezone.timedelta(
            minutes=window_minutes
        )
        attempt_count = FailedLoginAttempt.objects.filter(
            user=self.user,
            website=self.website,
            timestamp__gte=time_threshold
        ).count()
        return attempt_count >= max_attempts

    def clear_attempts(self):
        """
        Clears all failed login attempts for the user on the website.
        Useful after successful login.
        """
        FailedLoginAttempt.objects.filter(
            user=self.user,
            website=self.website
        ).delete()

    @staticmethod
    def log(user, website, ip=None, user_agent=None):
        geo = GeoService.get_geo(ip)
        return FailedLoginAttempt.objects.create(
            user=user,
            website=website,
            ip_address=ip,
            user_agent=user_agent,
            **geo,
        )