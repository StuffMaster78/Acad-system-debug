from celery import shared_task
from django.utils import timezone
from django.apps import apps

@shared_task
def cleanup_soft_deleted_models():
    """
    Runs force_delete_if_expired on all models that inherit from DeletionMixin
    and have expired deletion grace periods.
    """
    now = timezone.now()
    deleted_total = 0

    # List all models to check — you can expand this.
    model_names = [
        "users.User",
        "writer_management.Writer",
        "client_management.Client",
    ]

    for model_path in model_names:
        model = apps.get_model(model_path)
        expired = model.objects.filter(
            is_deletion_requested=True,
            deletion_scheduled__lte=now,
            deleted_at__isnull=True,
        )

        for obj in expired:
            obj.force_delete_if_expired()
            deleted_total += 1

    return f"Soft-deleted {deleted_total} expired account(s)."