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
    Expire referral bonuses that have expired.
    
    Note: ReferralBonus model doesn't have expires_at field.
    This is a placeholder task that can be implemented when
    expiration logic is added to the model.
    """
    try:
        # ReferralBonus model doesn't have expires_at field
        # This task is a placeholder for future implementation
        logger.debug("expire_referral_bonus task called (no-op: ReferralBonus has no expires_at field)")
        return 0
    except Exception as exc:
        logger.error("Error in expire_referral_bonus task: %s", exc)
        # Don't raise - just log the error to prevent task failures
        return 0


@shared_task(name="client_wallet.tasks.adjust_wallet_balance_for_referrals")
def adjust_wallet_balance_for_referrals():
    """
    Placeholder task for adjusting wallet balances based on referral bonuses.

    Currently a no-op that just logs; safe to extend later.
    """
    logger.debug("Running adjust_wallet_balance_for_referrals (no-op placeholder).")
    return "ok"


@shared_task(name="client_wallet.tasks.check_and_update_loyalty_points")
def check_and_update_loyalty_points():
    """
    Placeholder task for checking and updating loyalty points.

    Currently a no-op that just logs; safe to extend later.
    """
    logger.debug("Running check_and_update_loyalty_points (no-op placeholder).")
    return "ok"


