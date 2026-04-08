from datetime import timedelta

from django.utils import timezone

from authentication.models.failed_login_attempts import FailedLoginAttempt


def list_recent_failed_logins(
    *,
    user,
    website,
    window_minutes: int = 15,
):
    """
    Return recent failed login attempts for a user.
    """
    threshold = timezone.now() - timedelta(minutes=window_minutes)

    return FailedLoginAttempt.objects.filter(
        user=user,
        website=website,
        timestamp__gte=threshold,
    ).order_by("-timestamp")


def count_recent_failed_logins(
    *,
    user,
    website,
    window_minutes: int = 15,
) -> int:
    """
    Return recent failed login count for a user.
    """
    return list_recent_failed_logins(
        user=user,
        website=website,
        window_minutes=window_minutes,
    ).count()


def list_failed_logins_for_ip(
    *,
    website,
    ip_address: str,
    window_minutes: int = 15,
):
    """
    Return failed logins for an IP within a time window.
    """
    threshold = timezone.now() - timedelta(minutes=window_minutes)

    return FailedLoginAttempt.objects.filter(
        website=website,
        ip_address=ip_address,
        timestamp__gte=threshold,
    ).order_by("-timestamp")