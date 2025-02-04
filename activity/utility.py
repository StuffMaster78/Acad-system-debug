from .models import ActivityLog

def log_activity(user, action_type, description, metadata=None):
    """
    Logs an activity event in the system.
    """
    ActivityLog.objects.create(
        user=user,
        action_type=action_type,
        description=description,
        metadata=metadata or {}
    )