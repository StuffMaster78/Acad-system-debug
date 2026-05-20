"""Signals for referral code lifecycle."""

import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from referrals.models import ReferralCode
from referrals.services.referral_service import ReferralService

logger = logging.getLogger(__name__)

User = settings.AUTH_USER_MODEL


@receiver(post_save, sender=User)
def auto_generate_referral_code_for_clients(
    sender,
    instance,
    created,
    **kwargs,
):
    """
    Generate referral codes for clients once tenant context exists.

    A client may be created before website assignment during tests, imports,
    or staged onboarding. In that case we defer quietly and create the code
    on the later save that attaches the website.
    """
    if instance.role != "client":
        return

    if not instance.website:
        logger.debug(
            "Referral code generation deferred for client %s: no website.",
            instance.id,
        )
        return

    if ReferralCode.objects.filter(user=instance).exists():
        return

    try:
        code = ReferralService.generate_unique_code(
            instance,
            instance.website,
        )
        ReferralCode.objects.create(
            user=instance,
            website=instance.website,
            code=code,
        )
        logger.info(
            "Auto-generated referral code %s for client %s.",
            code,
            instance.id,
        )
    except Exception:
        logger.exception(
            "Failed to auto-generate referral code for client %s.",
            instance.id,
        )
