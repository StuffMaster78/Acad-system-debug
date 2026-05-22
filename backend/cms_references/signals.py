"""
Signals for cms_references.
Auto-update reference usage counts when citations change.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from cms_references.models import Citation, Reference


@receiver(post_save, sender=Citation)
@receiver(post_delete, sender=Citation)
def update_reference_usage_count(sender, instance, **kwargs):
    """Recalculate usage_count on the Reference when Citations change."""
    try:
        ref = instance.reference
        ref.usage_count = ref.citations.count()
        ref.save(update_fields=["usage_count"])
    except Reference.DoesNotExist:
        pass