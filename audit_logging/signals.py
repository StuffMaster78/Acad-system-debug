from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.apps import apps
from django.db import connection
from django.db.utils import ProgrammingError, OperationalError
import sys
from django.conf import settings

from audit_logging.services.audit_log_service import AuditLogService
from audit_logging.utils import get_current_request

EXCLUDED_MODELS = {"AuditLogEntry", "WebhookAuditLog"}


def is_excluded_model(sender) -> bool:
    """
    Check if a model should be excluded from audit logging.
    """
    return sender.__name__ in EXCLUDED_MODELS or sender._meta.abstract


def _contenttypes_table_ready() -> bool:
    """Return True if django_content_type table exists (safe during migrations)."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM information_schema.tables WHERE table_name = %s",
                ["django_content_type"],
            )
            return cursor.fetchone() is not None
    except (ProgrammingError, OperationalError):
        return False
    except Exception:
        return False


def _should_skip_signal() -> bool:
    """
    Skip audit logging while apps/tables are not ready (e.g., during initial migrate).
    """
    # If running management commands like migrate, avoid side effects
    if any(cmd in sys.argv for cmd in ("migrate", "makemigrations", "collectstatic")):
        # Only allow if contenttypes table is already present
        return not _contenttypes_table_ready()
    # In normal runtime, ensure contenttypes is installed and table exists
    if not apps.is_installed("django.contrib.contenttypes"):
        return True
    return not _contenttypes_table_ready()


@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    """
    Signal to log model create/update events.
    """
    if getattr(settings, "DISABLE_AUDIT_LOG_SIGNALS", False):
        return
    if is_excluded_model(sender) or _should_skip_signal():
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
    if getattr(settings, "DISABLE_AUDIT_LOG_SIGNALS", False):
        return
    if is_excluded_model(sender) or _should_skip_signal():
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