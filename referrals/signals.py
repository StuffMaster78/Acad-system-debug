from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Referral, Wallet, WalletTransaction, ReferralBonusConfig
from django.db import transaction
from django.core.mail import send_mail
from users.models import User
from django.conf import settings
from datetime import timedelta
from orders.models import Order
from order_payments_management.models import OrderPayment


@receiver(post_save, sender=Referral)
def credit_referral_bonus_on_order_completion(sender, instance, created, **kwargs):
    """
    Credit the referral bonus once the referred user places and pays for an order
    without refunds.
    """
    if created:
        # Check if the referral bonus has already been credited
        if instance.first_order_referral_bonus_credited:
            return

        # Check if the referred user has placed and paid for an order without a refund
        if instance.referred_user.has_paid_order_without_refund():
            # Fetch referral bonus configuration
            bonus_config = ReferralBonusConfig.objects.filter(website=instance.website).first()

            if not bonus_config:
                return

            # Ensure transaction is atomic
            with transaction.atomic():
                # Create or fetch wallet for the referrer
                wallet, _ = Wallet.objects.get_or_create(user=instance.referrer)

                # Calculate expiration time for the bonus
                expires_at = now() + timedelta(days=bonus_config.bonus_expiry_days)

                # Create a wallet transaction for the referral bonus
                WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='referral_bonus',
                    amount=bonus_config.registration_referral_bonus,
                    description="Referral Bonus: Successful Registration",
                    expires_at=expires_at,
                    website=instance.website,
                )

                # Mark the referral as bonus credited
                instance.first_order_referral_bonus_credited = True
                instance.save()

                # Send an email notification to the referrer
                send_referral_bonus_credited_email(instance.referrer, bonus_config.registration_referral_bonus)


def send_referral_bonus_credited_email(referrer, bonus_amount):
    """Send an email notification to the referrer when their bonus is credited."""
    subject = "Referral Bonus Credited"
    message = f"Hello {referrer.first_name},\n\nYour referral bonus of {bonus_amount} has been credited to your wallet."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [referrer.email]

    send_mail(subject, message, from_email, recipient_list)


@receiver(post_save, sender=OrderPayment)
def check_payment_and_credit_referral(sender, instance, created, **kwargs):
    """
    Check if the order payment is completed and credit the referral bonus
    if the referred user has paid for the order without refunds.
    """
    if created and instance.status == 'completed' and instance.order:
        order = instance.order
        referral = Referral.objects.filter(referred_user=order.client).first()

        if referral and not referral.first_order_referral_bonus_credited:
            # Fetch referral bonus configuration
            bonus_config = ReferralBonusConfig.objects.filter(website=referral.website).first()

            if not bonus_config:
                return

            # Check if the order was paid and has no refunds
            if order.is_paid() and not order.has_refunds():
                # Ensure transaction is atomic
                with transaction.atomic():
                    # Create or fetch wallet for the referrer
                    wallet, _ = Wallet.objects.get_or_create(user=referral.referrer)

                    # Calculate expiration time for the bonus
                    expires_at = now() + timedelta(days=bonus_config.bonus_expiry_days)

                    # Create a wallet transaction for the referral bonus
                    WalletTransaction.objects.create(
                        wallet=wallet,
                        transaction_type='referral_bonus',
                        amount=bonus_config.registration_referral_bonus,
                        description="Referral Bonus: Successful Registration",
                        expires_at=expires_at,
                        website=referral.website,
                    )

                    # Mark the referral as bonus credited
                    referral.first_order_referral_bonus_credited = True
                    referral.save()

                    # Send an email notification to the referrer
                    send_referral_bonus_credited_email(referral.referrer, bonus_config.registration_referral_bonus)


@receiver(post_save, sender=WalletTransaction)
def handle_wallet_transaction(sender, instance, created, **kwargs):
    """
    Handle the wallet transactions, particularly for referral bonuses.
    """
    if created and instance.transaction_type == 'referral_bonus':
        # Send an email to notify the user about their wallet transaction.
        send_wallet_transaction_email(instance.wallet.user, instance)


def send_wallet_transaction_email(user, transaction):
    """Send email to the user about their wallet transaction."""
    subject = f"Wallet Transaction: {transaction.transaction_type}"
    message = f"Hello {user.first_name},\n\nA {transaction.transaction_type} of {transaction.amount} has been made to your wallet. " \
              f"Your new balance is {transaction.wallet.balance}."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)
