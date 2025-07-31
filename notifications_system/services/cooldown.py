from django.utils.timezone import now
from datetime import timedelta
from notifications_system.models.notifications import Notification

def should_throttle_user(user, event, cooldown_secs=3600):
    """
    Checks if a user has triggered an event within the cooldown period.
    Args:
        user: User object
        event: Event type (string)
        cooldown_secs: Cooldown period in seconds
    Returns:
        bool: True if the user has triggered the event recently, False otherwise
    """
    recent = Notification.objects.filter(
        user=user, event=event,
        created_at__gte=now() - timedelta(seconds=cooldown_secs)
    ).exists()
    return recent