from celery import shared_task
from django.contrib.auth import get_user_model
from websites.models import Website
from activity.services.logger import ActivityLogger
import logging

logger = logging.getLogger("activity")


@shared_task
def async_log_activity(
    user_id=None,
    website_id=None,
    action_type=None,
    description=None,
    metadata=None,
    triggered_by_id=None,
):
    """Log an activity asynchronously using Celery.

    Args:
        user_id (int, optional): ID of the user the action is attributed to.
        website_id (int): ID of the associated website.
        action_type (str): Type of activity (e.g., "ORDER", "USER").
        description (str): Human-readable description of the event.
        metadata (dict, optional): Additional context (e.g., order_id).
        triggered_by_id (int, optional): ID of the actor who triggered the action.

    Returns:
        None
    """
    User = get_user_model()

    website = Website.objects.filter(id=website_id).first()
    if not website or not action_type or not description:
        logger.warning(
            "async_log_activity skipped due to missing core parameters. "
            f"website_id={website_id}, action_type={action_type}, "
            f"description={description}"
        )
        return

    user = User.objects.filter(id=user_id).first() if user_id else None
    triggered_by = None
    if triggered_by_id:
        triggered_by = User.objects.filter(id=triggered_by_id).first()

    ActivityLogger.log(
        user=user,
        website=website,
        action_type=action_type,
        description=description,
        metadata=metadata or {},
        triggered_by=triggered_by,
    )

    logger.info(
        "[Async ActivityLog] action_type=%s website_id=%s description=%s",
        action_type,
        website.id,
        description[:50],
    )