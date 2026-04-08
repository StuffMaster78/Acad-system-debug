from django.conf import settings
from django.db import models
from django.utils import timezone


class FailedLoginAttempt(models.Model):
    """
    Represent a failed login attempt for a user on a specific website.

    This model is used to track authentication failures for security
    monitoring and lockout enforcement.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="failed_login_attempts",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="failed_login_attempts",
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Time when the failed login attempt occurred.",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address from which the failed login occurred.",
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="User agent associated with the failed login attempt.",
    )
    city = models.CharField(
        max_length=128,
        null=True,
        blank=True,
    )
    region = models.CharField(
        max_length=128,
        null=True,
        blank=True,
    )
    country = models.CharField(
        max_length=128,
        null=True,
        blank=True,
    )
    asn = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="Autonomous System Number, if available.",
    )

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "website", "timestamp"]),
            models.Index(fields=["website", "timestamp"]),
            models.Index(fields=["ip_address", "timestamp"]),
        ]
        verbose_name = "Failed Login Attempt"
        verbose_name_plural = "Failed Login Attempts"

    def __str__(self) -> str:
        """
        Return a human-readable representation of the failed attempt.
        """
        return (
            f"Failed login for {self.user} "
            f"on {self.website} at {self.timestamp}"
        )

    @classmethod
    def is_locked_out(
        cls,
        *,
        user,
        website,
        window_minutes: int = 15,
        max_attempts: int = 5,
    ) -> bool:
        """
        Determine whether a user is locked out for a given website.

        Args:
            user: The user being checked.
            website: The website or tenant context.
            window_minutes: Time window to consider for failures.
            max_attempts: Maximum allowed failed attempts in the window.

        Returns:
            True if the user is locked out, otherwise False.
        """
        time_threshold = timezone.now() - timezone.timedelta(
            minutes=window_minutes,
        )

        recent_attempts = cls.objects.filter(
            user=user,
            website=website,
            timestamp__gte=time_threshold,
        ).count()

        return recent_attempts >= max_attempts