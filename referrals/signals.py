from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from .models import Referral, ReferralCode


@receiver(post_save, sender=User)
def create_referral_on_registration(sender, instance, created, **kwargs):
    """
    Create a referral record when a user registers with a referral code.
    """
    if created and instance.referred_by:
        referral = Referral.objects.create(
            referrer=instance.referred_by,
            referee=instance,
            referral_code=instance.referred_by.referral_code.code if hasattr(instance.referred_by, "referral_code") else None,
            website=instance.website,
        )
        referral.save()


@receiver(post_save, sender=User)
def generate_referral_code_on_registration(sender, instance, created, **kwargs):
    """
    Generate a referral code for the user after they register.
    """
    if created and not hasattr(instance, "referral_code"):
        code = f"REF-{instance.id}-{instance.date_joined.strftime('%Y%m%d%H%M%S')}"
        ReferralCode.objects.create(user=instance, code=code, website=instance.website)