from celery import shared_task
from celery.utils.log import get_task_logger

from communications.models import CommunicationMessage
from communications.utils import generate_preview_metadata

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def generate_link_preview_task(self, message_id):
    try:
        msg = CommunicationMessage.objects.get(id=message_id)

        link_url = getattr(msg, "link_url", None)
        if not link_url:
            return

        preview_failed_at = getattr(msg, "preview_failed_at", None)
        if preview_failed_at:
            logger.info(
                "Skipping preview for message %s — previous failure at %s",
                message_id,
                preview_failed_at,
            )
            return

        metadata = generate_preview_metadata(link_url)
        update_fields = []
        if metadata:
            msg.link_preview_json = metadata
            update_fields.append("link_preview_json")
            if hasattr(msg, "preview_failed_at"):
                msg.preview_failed_at = None
                update_fields.append("preview_failed_at")
            if update_fields:
                msg.save(update_fields=update_fields)
            logger.info("Preview generated for message %s", message_id)
        else:
            if hasattr(msg, "preview_failed_at"):
                from django.utils import timezone

                msg.preview_failed_at = timezone.now()
                msg.save(update_fields=["preview_failed_at"])
            logger.warning("Preview metadata missing for message %s", message_id)

    except CommunicationMessage.DoesNotExist:
        logger.warning("Message %s no longer exists.", message_id)
    except Exception as exc:
        logger.error("Preview failed for %s: %s", message_id, exc)
        raise self.retry(exc=exc)
