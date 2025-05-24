import logging

from celery import shared_task
from django.utils.timezone import now
from audit_logging.models import AuditLogEntry

logger = logging.getLogger("audit")


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def async_log_audit(
    self,
    action: str,
    target: str = "",
    target_id: int = None,
    actor_id: int = None,
    metadata: dict = None,
    ip_address: str = None,
    user_agent: str = None,
):
    """
    Celery task to log an audit event asynchronously.

    Retries up to 3 times with a 5-second delay on failure.

    Args:
        self (Task): The Celery task instance.
        action (str): The action performed (e.g., CREATE, DELETE).
        target (str): The model name in 'app.Model' format.
        target_id (int, optional): The ID of the target object.
        actor_id (int, optional): The ID of the user who performed it.
        metadata (dict, optional): Extra context for the log.
        ip_address (str, optional): IP address from the request.
        user_agent (str, optional): Client user-agent string.

    Raises:
        self.retry: Retries the task on exception.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()
    actor = None

    if actor_id:
        try:
            actor = User.objects.get(pk=actor_id)
        except User.DoesNotExist:
            logger.warning(
                "[AUDIT] Actor with user_id=%s does not exist.", actor_id
            )

    try:
        AuditLogEntry.objects.create(
            action=action,
            actor=actor,
            target=target,
            target_id=target_id,
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=now(),
        )

        logger.info(
            "[AUDIT] Async log complete: %s on %s(%s)",
            action, target, target_id
        )

    except Exception as exc:
        logger.error(
            "[AUDIT] Async log failed for %s on %s(%s): %s. Retrying...",
            action, target, target_id, str(exc)
        )
        raise self.retry(exc=exc)