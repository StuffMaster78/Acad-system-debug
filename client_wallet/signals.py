from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ClientWallet, ClientWalletTransaction, LoyaltyTransaction 
from referrals.models import Referral
from django.db import transaction

# Signal to update loyalty points after a payment is made
@receiver(post_save, sender=ClientWalletTransaction)
def update_loyalty_points_on_payment(sender, instance, created, **kwargs):
    """
    This signal listens for a new payment transaction and updates loyalty points.
    It assumes that loyalty points are awarded for 'payment' transactions.
    """
    if created and instance.transaction_type == 'payment':
        # Logic to add loyalty points after a payment transaction
        instance.wallet.loyalty_points.add_points_from_payment(instance.amount)

# Signal to update the referral stats after a new referral bonus is granted
@receiver(post_save, sender=Referral)
def update_referral_stats(sender, instance, created, **kwargs):
    """
    Updates referral stats when a new referral bonus is added.
    """
    if created:
        # Logic to update referral stats (could involve incrementing referral counts, etc.)
        instance.referrer.referral_stats.increment_referral_count()

# Signal to ensure that referral bonuses are adjusted when the wallet balance changes
@receiver(post_save, sender=ClientWallet)
def adjust_referral_bonus_on_wallet_change(sender, instance, created, **kwargs):
    """
    Adjusts referral bonuses when the wallet balance changes.
    This can be used to ensure bonus eligibility or deduction based on the balance.
    """
    if not created:
        # Logic to adjust referral bonus based on wallet balance changes (e.g., thresholds)
        pass  # Add your custom logic here

# Signal to ensure proper logging of wallet transactions
@receiver(post_save, sender=ClientWalletTransaction)
def log_wallet_transaction(sender, instance, created, **kwargs):
    """
    Automatically logs wallet transactions for auditing purposes.
    """
    if created:
        # Log the transaction or perform other related actions
        pass  # Implement additional logging if necessary

# Signal to handle actions when a referral bonus is deleted
@receiver(post_delete, sender=Referral)
def handle_referral_bonus_deletion(sender, instance, **kwargs):
    """
    Handles actions when a referral bonus is deleted, e.g., decrement referral stats.
    """
    # Adjust stats or take necessary actions when a referral bonus is deleted
    instance.referrer.referral_stats.decrement_referral_count()