from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from .models import Website


def _should_auto_populate() -> bool:
    return getattr(settings, "AUTO_POPULATE_ACADEMIC_SETTINGS", True)


@receiver(post_save, sender=Website, dispatch_uid="auto_populate_academic_settings_on_site_create")
def auto_populate_academic_settings(sender, instance: Website, created: bool, **kwargs):
    if not created:
        return
    if not _should_auto_populate():
        return

    def _do_populate():
        try:
            # Use the service to populate defaults
            from order_configs.services.default_configs import populate_default_configs_for_website
            populate_default_configs_for_website(instance, skip_existing=True)
        except Exception:
            # Silent fail to avoid blocking website creation
            pass

    # Run after the transaction commits so Website exists firmly
    transaction.on_commit(_do_populate)


