import logging
from activity.tasks import async_log_activity

logger = logging.getLogger("activity")

def safe_log_activity(
    *,
    user,
    website,
    action_type,
    description,
    metadata=None,
    triggered_by=None
):
    """Try sync log, fallback to Celery if failure occurs."""
    from activity.services.logger import ActivityLogger

    # Get website from user if not provided
    if not website and user:
        website = getattr(user, "website", None)
    
    try:
        return ActivityLogger.log_activity(
            user=user,
            website=website,
            action_type=action_type,
            description=description,
            metadata=metadata,
            triggered_by=triggered_by
        )
    except Exception as e:
        logger.warning(f"[SAFE LOG] Sync log failed: {e}. Fallback to async.")
        async_log_activity.delay(
            user_id=getattr(user, "id", None),
            website_id=getattr(website, "id", None),
            action_type=action_type,
            description=description,
            metadata=metadata,
            triggered_by_id=getattr(triggered_by, "id", None)
        )