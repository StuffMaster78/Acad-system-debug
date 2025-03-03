from celery import shared_task
from django.utils.timezone import now
from wallet.models import WalletTransaction

@shared_task
def expire_referral_bonuses():
    """Expire referral bonuses that have passed their expiration date."""
    expired_bonuses = WalletTransaction.objects.filter(
        transaction_type='bonus',
        expires_at__lte=now()
    )
    
    count = expired_bonuses.count()
    expired_bonuses.delete()
    
    return f"Expired {count} referral bonuses."