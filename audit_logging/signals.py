from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from audit_logging.services.audit_log_service import AuditLogService
from audit_logging.utils import get_current_request

EXCLUDED_MODELS = {"AuditLogEntry", "WebhookAuditLog"}


def is_excluded_model(sender) -> bool:
    """
    Check if a model should be excluded from audit logging.
    """
    return sender.__name__ in EXCLUDED_MODELS or sender._meta.abstract


@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    """
    Signal to log model create/update events.
    """
    if is_excluded_model(sender):
        return

    action = "CREATE" if created else "UPDATE"

    user = (
        getattr(instance, "updated_by", None)
        or getattr(instance, "created_by", None)
    )

    request = get_current_request()

    AuditLogService.log_from_signal(
        action=action,
        sender=sender,
        instance=instance,
        user=user,
        request=request,
    )


@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    """
    Signal to log model delete events.
    """
    if is_excluded_model(sender):
        return

    user = getattr(instance, "deleted_by", None)
    request = get_current_request()

    AuditLogService.log_from_signal(
        action="DELETE",
        sender=sender,
        instance=instance,
        user=user,
        request=request,
    )