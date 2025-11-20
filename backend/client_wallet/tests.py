from celery import shared_task
from datetime import timedelta
from client_wallet.models import ClientWallet, ReferralBonus
from django.utils.timezone import now

@shared_task
def expire_referral_bonus():
    """
    Task to expire referral bonuses after a certain time period.
    This can be triggered periodically (e.g., every night).
    """
    expiration_period = timedelta(days=30)  # Example: 30 days expiration period
    expiration_threshold = now() - expiration_period

    # Find all referral bonuses that are older than the expiration threshold
    expired_bonuses = ReferralBonus.objects.filter(
        created_at__lt=expiration_threshold, 
        is_expired=False
    )

    for bonus in expired_bonuses:
        bonus.is_expired = True
        bonus.save()

        # Optionally, notify the client about expired bonuses (e.g., send email)
        # send_email_notification(bonus.client)

@shared_task
def adjust_wallet_balance_for_referrals():
    """
    Task to adjust the wallet balance based on referral bonuses periodically.
    """
    # Add logic to adjust wallet balances if needed (e.g., transferring referral bonuses)
    for wallet in ClientWallet.objects.all():
        referral_bonus = wallet.user.referral_bonus  # Example logic to find referral bonus
        if referral_bonus and not referral_bonus.is_expired:
            # Adjust wallet balance based on referral bonus or logic
            wallet.balance += referral_bonus.amount
            wallet.save()

@shared_task
def check_and_update_loyalty_points():
    """
    Periodically update loyalty points based on client activities.
    """
    for wallet in ClientWallet.objects.all():
        # Add logic for periodic loyalty points adjustments (e.g., rewards for activity)
        pass