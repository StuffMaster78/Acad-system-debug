from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import PricingConfiguration

CACHE_KEY_PREFERRED_WRITER_COST = "preferred_writer_cost"

@receiver(post_save, sender=PricingConfiguration)
def clear_preferred_writer_cost_cache(sender, instance, **kwargs):
    """
    Clear the preferred writer cost cache when PricingConfig is saved.
    """
    cache.delete(CACHE_KEY_PREFERRED_WRITER_COST)