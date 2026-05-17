from django.utils import timezone


def now():
    """
    Centralized time provider.
    """

    return timezone.now()