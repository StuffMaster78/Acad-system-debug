from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Referral, Wallet, WalletTransaction, ReferralBonusConfig
from django.db import transaction
from django.core.mail import send_mail
from users.models import User
from django.conf import settings
from django.conf import settings as dj_settings
from datetime import timedelta
from orders.models import Order
from order_payments_management.models import OrderPayment


@receiver(post_save, sender=Referral)
def credit_referral_bonus_on_order_completion(sender, instance, created, **kwargs):
    if getattr(dj_settings, "DISABLE_REFERRAL_SIGNALS", False):
        return
    """
    Credit the referral bonus once the referred user places and pays for an order
    without refunds.
    """
    if created:
        # Check if the referral bonus has already been credited
        if getattr(instance, 'first_order_bonus_credited', False):
            return

        # Check if the referred user (referee) has placed and paid for an order without a refund
        # Check if referee has any paid orders without refunds
        has_paid_order = False
        if instance.referee:
            # Check if referee has any orders that are paid and not refunded
            from orders.models import Order
            paid_orders = Order.objects.filter(
                client=instance.referee,
                is_paid=True
            )
            for order in paid_orders:
                # Check if order has no refunds
                has_refunds = False
                if order.payments.exists():
                    has_refunds = order.payments.filter(status='refunded').exists() or \
                                 order.payments.filter(payment_refunds__status='processed').exists()
                if not has_refunds:
                    has_paid_order = True
                    break
        
        if has_paid_order:
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
                    amount=bonus_config.first_order_bonus,
                    description="Referral Bonus: Successful Registration",
                    expires_at=expires_at,
                    website=instance.website,
                )

                # Mark the referral as bonus credited
                instance.first_order_bonus_credited = True
                instance.save()

                # Send an email notification to the referrer
                send_referral_bonus_credited_email(instance.referrer, bonus_config.first_order_bonus)


def send_referral_bonus_credited_email(referrer, bonus_amount):
    """Send an email notification to the referrer when their bonus is credited."""
    subject = "Referral Bonus Credited"
    message = f"Hello {referrer.first_name},\n\nYour referral bonus of {bonus_amount} has been credited to your wallet."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [referrer.email]

    send_mail(subject, message, from_email, recipient_list)


@receiver(post_save, sender=OrderPayment)
def check_payment_and_credit_referral(sender, instance, created, **kwargs):
    if getattr(dj_settings, "DISABLE_REFERRAL_SIGNALS", False):
        return
    """
    Check if the order payment is completed and credit the referral bonus
    if the referred user has paid for the order without refunds.
    """
    if created and instance.status == 'completed' and instance.order:
        order = instance.order
        # Find referral where the order client is the referee
        # Order model uses 'client' field for the client who placed the order
        order_client = getattr(order, 'client', None)
        if not order_client:
            return
        
        referral = Referral.objects.filter(referee=order_client).first()

        if referral and not getattr(referral, 'first_order_bonus_credited', False):
            # Fetch referral bonus configuration
            bonus_config = ReferralBonusConfig.objects.filter(website=referral.website).first()

            if not bonus_config:
                return

            # Check if the order was paid and has no refunds
            # is_paid is a boolean field, not a method
            is_paid = getattr(order, 'is_paid', False)
            # Check for refunds by looking at payment refunds
            has_refunds = False
            if order.payments.exists():
                # Check if any payment has been refunded
                has_refunds = order.payments.filter(status='refunded').exists() or \
                             order.payments.filter(payment_refunds__status='processed').exists()
            
            if is_paid and not has_refunds:
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
                        amount=bonus_config.first_order_bonus,
                        description="Referral Bonus: Successful Registration",
                        expires_at=expires_at,
                        website=referral.website,
                    )

                    # Mark the referral as bonus credited
                    referral.first_order_bonus_credited = True
                    referral.save()

                    # Send an email notification to the referrer
                    send_referral_bonus_credited_email(referral.referrer, bonus_config.first_order_bonus)


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
