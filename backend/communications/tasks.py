from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from communications.models import CommunicationMessage
from communications.utils import generate_preview_metadata
from communications.models import (
    CommunicationLog, SystemAlert
)
from django.contrib.auth import get_user_model

User = get_user_model()

logger = get_task_logger(__name__)

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 5}
)
def generate_link_preview_task(self, message_id):
    try:
        msg = CommunicationMessage.objects.get(id=message_id)

        # Already failed previously, don't retry unless manually reset
        if msg.preview_failed_at:
            logger.info(f"Skipping preview for message {message_id} due to previous failure at {msg.preview_failed_at}")
            return

        if msg.link_url:
            metadata = generate_preview_metadata(msg.link_url)
            if metadata:
                msg.link_preview_json = metadata
                msg.preview_failed_at = None
                msg.save(update_fields=["link_preview_json", "preview_failed_at"])
                logger.info(f"Preview generated for message {message_id}")
            else:
                msg.preview_failed_at = timezone.now()
                msg.save(update_fields=["preview_failed_at"])
                logger.warning(f"Preview metadata missing for message {message_id}")
    except CommunicationMessage.DoesNotExist:
        logger.warning(f"Message {message_id} no longer exists.")
    except Exception as e:
        logger.error(f"Preview failed for {message_id}: {e}")
        raise self.retry(exc=e)
    


@shared_task
def track_audit_log_access(
    user_id, accessed_at=None, is_impersonated=False
):
    """ 
    Track access to audit logs and flag suspicious behavior.
    """
    accessed_at = accessed_at or timezone.now()

    user = User.objects.filter(id=user_id).first()
    if not user:
        return

    # Example: count last 5 minutes of hits
    recent_logs = CommunicationLog.objects.filter(
        user=user,
        action="view_audit_log",
        created_at__gte=accessed_at - timezone.timedelta(minutes=5)
    ).count()

    # Optional: flag suspicious behavior
    if recent_logs > 20 or is_impersonated:
        SystemAlert.objects.create(
            category="audit_access",
            severity="high",
            triggered_by=user,
            title="Suspicious audit log access",
            message=(
                f"{user.get_display_name()} accessed audit logs "
                f"{recent_logs} times in under 5 minutes. "
                f"{'While impersonating.' if is_impersonated else ''}"
            )
        )


