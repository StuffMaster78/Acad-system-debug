# from celery import shared_task
# from django.utils.timezone import now
# from client_wallet.models import ReferralBonus

# @shared_task
# def expire_referral_bonuses():
#     expired_bonuses = ReferralBonus.objects.filter(expires_at__lt=now(), is_deleted=False)
#     for bonus in expired_bonuses:
#         bonus.soft_delete()