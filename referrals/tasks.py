from celery import shared_task
from django.utils.timezone import now
from .models import WalletTransaction
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from referrals.models import ReferralBonusDecay

@shared_task
def expire_referral_bonuses():
    """
    This task checks all referral bonuses and expires them if the expiration date has passed.
    """
    # Get the referral bonuses that have expired
    expired_wallet_transactions = WalletTransaction.objects.filter(
        transaction_type='referral_bonus',
        expires_at__lte=now(),
        is_expired=False  # Assuming we have a flag to mark expiration
    )

    for transaction in expired_wallet_transactions:
        # Mark the transaction as expired (soft delete)
        transaction.is_expired = True
        transaction.save()

        # Optionally send an email notifying the user that their referral bonus expired
        send_referral_bonus_expired_email(transaction.wallet.user)

    return f"Expired {expired_wallet_transactions.count()} referral bonuses."


def send_referral_bonus_expired_email(user):
    """Send an email notification to the user when their referral bonus expires."""
    subject = "Referral Bonus Expired"
    message = f"Hello {user.first_name},\n\nYour referral bonus has expired and is no longer available."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)


@shared_task
def notify_referral_bonus_expiration():
    """
    This task notifies users 24 hours before their referral bonus expires.
    """
    # Find referral bonuses that are about to expire in 24 hours
    soon_to_expire_wallet_transactions = WalletTransaction.objects.filter(
        transaction_type='referral_bonus',
        expires_at__lte=now() + timedelta(days=1),
        expires_at__gt=now(),
        is_expired=False  # Not yet expired
    )

    for transaction in soon_to_expire_wallet_transactions:
        # Send an email reminder
        send_referral_bonus_expiration_warning_email(transaction.wallet.user)

    return f"Sent expiration warning for {soon_to_expire_wallet_transactions.count()} referral bonuses."


def send_referral_bonus_expiration_warning_email(user):
    """Send an email reminder when the referral bonus is close to expiration."""
    subject = "Referral Bonus Expiring Soon"
    message = f"Hello {user.first_name},\n\nYour referral bonus is about to expire in 24 hours. Please make use of it before it expires!"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)


@shared_task
def decay_referral_bonuses():
    """
    Periodic task to decay referral bonuses as they approach expiration (if applicable).
    """
    # Fetch referral bonuses nearing expiration but not yet expired
    nearing_expiry_wallet_transactions = WalletTransaction.objects.filter(
        transaction_type='referral_bonus',
        expires_at__lte=now() + timedelta(days=2),  # Adjust threshold as needed
        expires_at__gt=now(),
        is_expired=False,
        decay_percentage__gt=0  # Assuming we have a decay_percentage field
    )

    for transaction in nearing_expiry_wallet_transactions:
        decay_percentage = transaction.decay_percentage or 0  # Add decay percentage logic here
        # Apply decay to the bonus amount
        transaction.amount -= transaction.amount * (decay_percentage / 100)

        # Optionally, update the decay percentage or handle logic for progressive decay
        transaction.save()

        # Optional: Send an email notification about the bonus decay
        send_referral_bonus_decay_email(transaction.wallet.user, transaction.amount)

    return f"Decayed {nearing_expiry_wallet_transactions.count()} referral bonuses."

@shared_task
def apply_monthly_referral_bonus_decay():
    decays = ReferralBonusDecay.objects.all().select_related('wallet_transaction')
    for decay in decays:
        decay.apply_decay()

def send_referral_bonus_decay_email(user, new_amount):
    """Send an email notification about the decay of the referral bonus."""
    subject = "Your Referral Bonus Has Decayed"
    message = f"Hello {user.first_name},\n\nYour referral bonus has decreased in value due to the approaching expiration date. " \
              f"The new value of your bonus is {new_amount}."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)