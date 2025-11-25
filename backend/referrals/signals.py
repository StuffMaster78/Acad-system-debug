"""
Signals for referral system - auto-generate codes for clients
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from referrals.models import ReferralCode
from referrals.services.referral_service import ReferralService
import logging

logger = logging.getLogger(__name__)

User = settings.AUTH_USER_MODEL


@receiver(post_save, sender=User)
def auto_generate_referral_code_for_clients(sender, instance, created, **kwargs):
    """
    Automatically generate referral code when a client user is created.
    Only clients can have referral codes - admins, superadmins, support, editors, and writers cannot.
    """
    if not created:
        return
    
    # Only generate referral codes for clients
    if instance.role != 'client':
        return
    
    # Ensure user has a website
    if not instance.website:
        logger.warning(f"Cannot generate referral code for client {instance.id}: no website assigned")
        return
    
    # Check if referral code already exists
    try:
        existing_code = ReferralCode.objects.get(user=instance, website=instance.website)
        logger.debug(f"Referral code already exists for client {instance.id}: {existing_code.code}")
        return
    except ReferralCode.DoesNotExist:
        pass
    
    # Generate unique referral code
    try:
        code = ReferralService.generate_unique_code(instance, instance.website)
        ReferralCode.objects.create(
            user=instance,
            website=instance.website,
            code=code
        )
        logger.info(f"Auto-generated referral code {code} for client {instance.id}")
    except Exception as e:
        logger.error(f"Failed to auto-generate referral code for client {instance.id}: {e}", exc_info=True)
