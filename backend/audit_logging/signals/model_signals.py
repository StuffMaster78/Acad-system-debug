from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from audit_logging.factories.audit_event_factory import AuditEventFactory


def _safe_actor(instance):
    return getattr(instance, "updated_by_id", None) or getattr(instance, "created_by_id", None)


def _safe_website(instance):
    return getattr(instance, "website", None)


# -------------------------
# GENERIC POST SAVE AUDIT
# -------------------------

@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):

    if sender.__name__.startswith("Audit"):
        return

    try:
        AuditEventFactory.create(
            website=_safe_website(instance),
            actor_id=_safe_actor(instance),
            action=f"{sender.__name__.lower()}.created" if created else f"{sender.__name__.lower()}.updated",
            object_type=sender.__name__.lower(),
            object_id=str(getattr(instance, "id", None)),
            metadata={
                "model": sender.__name__,
            },
        )
    except Exception:
        pass


# -------------------------
# DELETE AUDIT
# -------------------------

@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):

    if sender.__name__.startswith("Audit"):
        return

    try:
        AuditEventFactory.create(
            website=_safe_website(instance),
            actor_id=_safe_actor(instance),
            action=f"{sender.__name__.lower()}.deleted",
            object_type=sender.__name__.lower(),
            object_id=str(getattr(instance, "id", None)),
        )
    except Exception:
        pass