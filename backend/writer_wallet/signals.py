from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WalletTransaction, WriterWallet, PaymentConfirmation
from django.conf import settings
from notifications_system.services.notification_service import (
    NotificationService
)
from wallet.services.wallet_transaction_service import WalletTransactionService

@receiver(post_save, sender=WalletTransaction)
def update_writer_wallet(sender, instance, created, **kwargs):
    """
    Updates the writer's wallet balance whenever a transaction is added.
    """
    if created:
        writer_wallet = instance.writer_wallet
        if instance.transaction_type in ["Earning", "Bonus", "Reward", "Adjustment"]:
            entry = WalletTransactionService.credit(
                user=writer_wallet.writer,
                website=writer_wallet.website,
                amount=instance.amount,
                description=f"Legacy writer wallet transaction {instance.transaction_type}",
                source="writer_wallet_signal",
                reference=instance.id,
                transaction_type="order_payment" if instance.transaction_type == "Earning" else "bonus",
                metadata={"legacy_transaction_type": instance.transaction_type},
            )
            writer_wallet.balance = entry.balance_after
            writer_wallet.total_earnings += instance.amount
        elif instance.transaction_type in ["Fine", "Refund Deduction", "Payout"]:
            entry = WalletTransactionService.debit(
                user=writer_wallet.writer,
                website=writer_wallet.website,
                amount=instance.amount,
                description=f"Legacy writer wallet transaction {instance.transaction_type}",
                source="writer_wallet_signal",
                reference=instance.id,
                transaction_type="payout" if instance.transaction_type == "Payout" else "fine",
                metadata={"legacy_transaction_type": instance.transaction_type},
            )
            writer_wallet.balance = entry.balance_after
            if instance.transaction_type == "Fine":
                writer_wallet.total_fines += instance.amount
        writer_wallet.save()


@receiver(post_save, sender=PaymentConfirmation)
def notify_admin_on_review_request(sender, instance, created, **kwargs):
    """
    Notifies admin if a writer requests a review of their payment.
    """
    if instance.requested_review and created:
        admin_emails = [admin.email for admin in WriterWallet.objects.filter(is_superuser=True)]
        NotificationService.notify(
            event_key="Payment_review_requested",
            website=instance.writer_wallet.writer.website,
            recipient=instance.writer_waller.writer,
            context={
                "from_email": "settings.DEFAULT_FROM_EMAIL",
                "user_name": "instance.writer_wallet.writer.username",
                "message": {f"Writer {instance.writer_wallet.writer.username} has requested a review of their payment."},
            },
            channels=["email", "in_app"],
            is_critical=True,
            is_broadcast=False,
            is_digest=False,
            is_silent=False,

        )
