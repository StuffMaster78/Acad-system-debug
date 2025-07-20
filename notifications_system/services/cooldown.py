from django.utils.timezone import now
from datetime import timedelta
from notifications_system.models.notifications import Notification

def should_throttle_user(user, event, cooldown_secs=3600):
    recent = Notification.objects.filter(
        user=user, event=event,
        created_at__gte=now() - timedelta(seconds=cooldown_secs)
    ).exists()
    return recent