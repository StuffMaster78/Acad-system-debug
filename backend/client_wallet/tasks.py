"""
Celery tasks for client wallet referral bonuses and loyalty points.

These are kept lightweight but fully registered so Celery beat schedules
in settings.CELERY_BEAT_SCHEDULE work without errors.
"""

from celery import shared_task
from django.utils.timezone import now
import logging

from client_wallet.models import ReferralBonus

logger = logging.getLogger(__name__)


@shared_task(name="client_wallet.tasks.expire_referral_bonus")
def expire_referral_bonus():
    """
    Soft-delete referral bonuses that have expired.
    """
    try:
        expired_bonuses = ReferralBonus.objects.filter(
            expires_at__lt=now(),
            is_deleted=False,
        )
        count = expired_bonuses.count()
        for bonus in expired_bonuses:
            bonus.soft_delete()
        logger.info("Expired %s referral bonuses", count)
        return count
    except Exception as exc:
        logger.error("Error expiring referral bonuses: %s", exc)
        raise


@shared_task(name="client_wallet.tasks.adjust_wallet_balance_for_referrals")
def adjust_wallet_balance_for_referrals():
    """
    Placeholder task for adjusting wallet balances based on referral bonuses.

    Currently a no-op that just logs; safe to extend later.
    """
    logger.info("Running adjust_wallet_balance_for_referrals (no-op placeholder).")
    return "ok"


@shared_task(name="client_wallet.tasks.check_and_update_loyalty_points")
def check_and_update_loyalty_points():
    """
    Placeholder task for checking and updating loyalty points.

    Currently a no-op that just logs; safe to extend later.
    """
    logger.info("Running check_and_update_loyalty_points (no-op placeholder).")
    return "ok"


