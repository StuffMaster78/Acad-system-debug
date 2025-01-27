from core.celery import shared_task
from .models import Referral, ReferralBonusConfig
from wallet.models import Wallet, WalletTransaction


@shared_task
def credit_referral_bonuses():
    """
    Periodically check and credit referral bonuses for pending referrals.
    """
    pending_referrals = Referral.objects.filter(registration_bonus_credited=False)
    for referral in pending_referrals:
        bonus_config = ReferralBonusConfig.objects.get(website=referral.website)
        wallet = Wallet.objects.get(user=referral.referrer)
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type="bonus",
            amount=bonus_config.registration_bonus,
            description="Referral Bonus: Successful Registration",
            website=referral.website,
        )
        referral.registration_bonus_credited = True
        referral.save()