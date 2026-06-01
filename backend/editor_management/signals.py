from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import EditorProfile
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@receiver(post_save, sender=User)
def create_editor_profile(sender, instance, created, **kwargs):
    """
    Automatically create an EditorProfile when a user with the role 'editor' is created.
    """
    if created and instance.role == "editor":
        EditorProfile.objects.create(user=instance, name=instance.username)



"""
editor_management/signals.py

Bootstrap EditorPerformance when EditorProfile is created.

FIX: EditorPerformance was not created on EditorProfile save.
This caused RelatedObjectDoesNotExist when editor.performance
was accessed before calculate_performance() ran.
"""




@receiver(post_save, sender="editor_management.EditorProfile")
def bootstrap_editor_performance(sender, instance, created, **kwargs):
    """
    Create EditorPerformance when EditorProfile is first created.
    Safe to call multiple times — uses get_or_create.
    """
    if not created:
        return

    try:
        from editor_management.models import EditorPerformance
        EditorPerformance.objects.get_or_create(
            editor=instance,
            defaults={
                "total_orders_reviewed": 0,
                "late_reviews": 0,
            },
        )
        logger.info(
            "EditorPerformance bootstrapped: editor=%s",
            instance.registration_id,
        )
    except Exception as exc:
        logger.exception(
            "bootstrap_editor_performance failed: editor=%s: %s",
            getattr(instance, "registration_id", "?"),
            exc,
        )