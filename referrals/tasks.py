# # from core.celery import shared_task
# import django_rq
# from django_q import job
# from .models import Referral, ReferralBonusConfig
# from wallet.models import Wallet, WalletTransaction


# @job
# def credit_referral_bonuses():
#     """
#     Periodically check and credit referral bonuses for pending referrals.
#     """
#     pending_referrals = Referral.objects.filter(registration_bonus_credited=False)
#     for referral in pending_referrals:
#         bonus_config = ReferralBonusConfig.objects.get(website=referral.website)
#         wallet = Wallet.objects.get(user=referral.referrer)
#         WalletTransaction.objects.create(
#             wallet=wallet,
#             transaction_type="bonus",
#             amount=bonus_config.registration_bonus,
#             description="Referral Bonus: Successful Registration",
#             website=referral.website,
#         )
#         referral.registration_bonus_credited = True
#         referral.save()


from celery import shared_task
from django.utils.timezone import now
from wallet.models import WalletTransaction

@shared_task
def expire_referral_bonuses():
    expired_bonuses = WalletTransaction.objects.filter(
        transaction_type="bonus", 
        expires_at__lte=now(), 
        is_expired=False
    )
    
    for bonus in expired_bonuses:
        bonus.is_expired = True
        bonus.save()
