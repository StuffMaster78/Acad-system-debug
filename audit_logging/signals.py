from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from audit_logging.tasks import log_audit_entry_task
from audit_logging.utils import get_client_ip, get_user_agent
from audit_logging.middleware import get_current_request

EXCLUDED_MODELS = {"AuditLog"}


def is_excluded_model(sender) -> bool:
    """
    Check if a model should be excluded from audit logging.

    Args:
        sender (Model): The model class sending the signal.

    Returns:
        bool: True if the model is excluded or abstract.
    """
    return sender.__name__ in EXCLUDED_MODELS or sender._meta.abstract


@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    """
    Logs creation or update of a model instance.

    Args:
        sender (Model): The model class.
        instance (Model): The object saved.
        created (bool): True if created, False if updated.
    """
    if is_excluded_model(sender):
        return

    model_name = sender.__name__
    app_label = sender._meta.app_label
    action = "CREATE" if created else "UPDATE"

    user = (
        getattr(instance, "updated_by", None)
        or getattr(instance, "created_by", None)
    )
    request = get_current_request()

    log_audit_entry_task.delay(
        action=action,
        target=f"{app_label}.{model_name}",
        target_id=instance.pk,
        actor_id=getattr(user, "id", None),
        metadata={"message": f"{model_name} was {action.lower()}d."},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )


@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    """
    Logs deletion of a model instance.

    Args:
        sender (Model): The model class.
        instance (Model): The object deleted.
    """
    if is_excluded_model(sender):
        return

    model_name = sender.__name__
    app_label = sender._meta.app_label
    user = getattr(instance, "deleted_by", None)
    request = get_current_request()

    log_audit_entry_task.delay(
        action="DELETE",
        target=f"{app_label}.{model_name}",
        target_id=instance.pk,
        actor_id=getattr(user, "id", None),
        metadata={"message": f"{model_name} was deleted."},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )