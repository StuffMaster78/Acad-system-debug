from django.db.models.signals import post_save
from django.dispatch import receiver
from wallet.models import WalletTransaction
from .models import Notification
from core.utils import send_notification

@receiver(post_save, sender=WalletTransaction)
def notify_wallet_transaction(sender, instance, created, **kwargs):
    """
    Create and send notifications when a wallet transaction occurs.
    """
    if created:
        Notification.objects.create(
            user=instance.wallet.user,
            type="in_app",
            title="Wallet Transaction",
            message=f"A transaction of ${instance.amount:.2f} was made on your wallet.",
            website=instance.wallet.website,
        )
        send_notification(
            instance.wallet.user,
            f"A transaction of ${instance.amount:.2f} was made on your wallet.",
            notification_type="email"
        )