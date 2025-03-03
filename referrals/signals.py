from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from .models import Referral, ReferralCode, ReferralBonusConfig
from wallet.models import Wallet, WalletTransaction


@receiver(post_save, sender=User)
def create_referral_on_registration(sender, instance, created, **kwargs):
    """
    Creates a referral record when a user registers using a referral code.
    Prevents self-referral.
    """
    if created and instance.referred_by:
        referrer = instance.referred_by

        # 🔴 Prevent self-referral
        if referrer == instance:
            return  # Do nothing if the user refers themselves

        # Ensure referral does not already exist
        if not Referral.objects.filter(referee=instance).exists():
            referral = Referral.objects.create(
                referrer=referrer,
                referee=instance,
                referral_code=referrer.referral_code.code if hasattr(referrer, "referral_code") else None,
                website=instance.website,
            )

            # Credit registration bonus if applicable
            bonus_config = ReferralBonusConfig.objects.filter(website=instance.website).first()
            if bonus_config and bonus_config.registration_bonus > 0:
                wallet, _ = Wallet.objects.get_or_create(user=referrer, website=instance.website)
                WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='bonus',
                    amount=bonus_config.registration_bonus,
                    description="Referral Bonus: Successful Registration",
                    website=instance.website,
                )

                # Mark the registration bonus as credited
                referral.registration_bonus_credited = True
                referral.save()


@receiver(post_save, sender=User)
def generate_referral_code_on_registration(sender, instance, created, **kwargs):
    """
    Generate a referral code for the user after they register.
    """
    if created and not hasattr(instance, "referral_code"):
        code = f"REF-{instance.id}-{instance.date_joined.strftime('%Y%m%d%H%M%S')}"
        ReferralCode.objects.create(user=instance, code=code, website=instance.website)
