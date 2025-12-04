from celery import shared_task
from django.utils import timezone
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

@shared_task
def cleanup_soft_deleted_models():
    """
    Runs force_delete_if_expired on all models that inherit from DeletionMixin
    and have expired deletion grace periods.
    
    For writers, this also handles WriterProfile cleanup since WriterProfile
    is linked to User via OneToOneField and doesn't directly inherit DeletionMixin.
    """
    now = timezone.now()
    deleted_total = 0

    # List all models to check — you can expand this.
    model_names = [
        "users.User",
        "client_management.Client",
    ]

    for model_path in model_names:
        try:
            model = apps.get_model(model_path)
        except LookupError:
            # Skip models that don't exist
            logger.warning(f"Model {model_path} not found, skipping...")
            continue
        
        expired = model.objects.filter(
            is_deletion_requested=True,
            deletion_scheduled__lte=now,
            deleted_at__isnull=True,
        )

        for obj in expired:
            # Handle deletion - force_delete_if_expired returns True if deletion occurred
            was_deleted = obj.force_delete_if_expired()
            
            # Special handling for writer users: also mark WriterProfile as deleted
            if model_path == "users.User" and obj.role == "writer":
                try:
                    writer_profile = obj.writer_profile
                    if not writer_profile.is_deleted:
                        writer_profile.is_deleted = True
                        writer_profile.deleted_at = now
                        writer_profile.save(update_fields=['is_deleted', 'deleted_at'])
                        logger.info(f"Marked WriterProfile as deleted for user {obj.id}")
                except AttributeError:
                    # WriterProfile might not exist (user might not have one)
                    pass
                except Exception as e:
                    # Other errors
                    logger.warning(f"Could not update WriterProfile for writer user {obj.id}: {e}")
            
            if was_deleted:
                deleted_total += 1

    return f"Soft-deleted {deleted_total} expired account(s)."