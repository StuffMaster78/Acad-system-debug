from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from authentication.models.mfa_settings import MFASettings

User = get_user_model()


@receiver(post_save, sender=User)
def ensure_mfa_settings_exist(sender, instance, created, **kwargs):
    """
    Ensure each user has an MFA settings record.
    """
    if not created:
        return

    website = getattr(instance, "website", None)
    if website is None:
        return

    MFASettings.objects.get_or_create(
        user=instance,
        website=website,
    )