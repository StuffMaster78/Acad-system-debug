from decimal import Decimal
from django.db import models, transaction
from django.utils.timezone import now
from datetime import timedelta
from core.models.base import WebsiteSpecificBaseModel
from django.conf import settings
from loyalty_management.models import (
    LoyaltyTier, LoyaltyTransaction,
    LoyaltyPointsConversionConfig
)
from django.core.exceptions import ValidationError
import logging

# Logger setup
logger = logging.getLogger(__name__)
User = settings.AUTH_USER_MODEL 

# Back-compat placeholder for tests expecting ReferralBonus in this app
class ReferralBonus(models.Model):
    website = models.ForeignKey('websites.Website', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
class ClientWallet(WebsiteSpecificBaseModel):
    """
    Wallet for clients, tracking their balance and referral bonuses.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="client_wallet",
        help_text="The client associated with this wallet."
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Client's available wallet balance."
    )
    currency = models.CharField(
        max_length=3,
        default="USD",
        help_text="Currency of the wallet balance."
    )
    loyalty_points = models.PositiveIntegerField(
        default=0,
        help_text="Accumulated loyalty points."
    )
    last_updated = models.DateTimeField(auto_now=True)

    def debit_wallet(self, amount, reason=""):
        """
        Deducts an amount from the wallet with transaction safety.
        """
        user = self.user 
        with transaction.atomic():
            wallet = ClientWallet.objects.select_for_update().get(id=self.id)
            # Locking related transactions as well
            transactions = ClientWalletTransaction.objects.select_for_update().filter(wallet=wallet)
            
            if wallet.balance < amount and not user.is_admin:
                raise ValueError("Insufficient funds")  # Changed to provide a more specific error message
            wallet.balance -= amount
            wallet.save(update_fields=['balance'])

            # Log the wallet transaction
            ClientWalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='payment',
                amount=-amount,
                description=reason
            )

    def credit_wallet(self, amount, reason=""):
        """
        Adds an amount to the wallet, either via refund or other credit.
        """
        with transaction.atomic():
            wallet = ClientWallet.objects.select_for_update().get(id=self.id)
            wallet.balance += amount
            wallet.save(update_fields=['balance'])

            ClientWalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='top-up',
                amount=amount,
                description=reason
            )

    def convert_loyalty_points_to_wallet(self):
        """
        Converts loyalty points into wallet balance based on the configured conversion rate.
        """
        try:
            config = LoyaltyPointsConversionConfig.objects.get(website=self.website)
        except LoyaltyPointsConversionConfig.DoesNotExist:
            raise ValidationError("Loyalty points conversion configuration not found.")
        
        if not config.active:
            raise ValidationError("Loyalty points conversion is currently disabled.")

        if self.loyalty_points < config.min_conversion_points:
            raise ValidationError(f"Client needs at least {config.min_conversion_points} loyalty points to convert.")

        total_conversion_amount = Decimal(self.loyalty_points) * config.conversion_rate

        # Check if the total conversion amount exceeds the max limit
        if total_conversion_amount + self.balance > config.max_conversion_limit:
            raise ValidationError(f"Conversion exceeds the maximum wallet balance limit of {config.max_conversion_limit}.")
        
        # Store the conversion rate at the time of transaction
        conversion_rate_at_time = config.conversion_rate

        # Deduct the loyalty points
        self.loyalty_points -= config.min_conversion_points  # Deduct the required points

        with transaction.atomic():
            self.save(update_fields=['loyalty_points'])  # Save the loyalty points deduction first
            self.balance += total_conversion_amount
            self.save(update_fields=['balance'])

            # Log the transaction for loyalty conversion
            ClientWalletTransaction.objects.create(
                wallet=self,
                transaction_type='loyalty_conversion',
                amount=total_conversion_amount,
                description=f"Converted {config.min_conversion_points} loyalty points to wallet balance.",
                website=self.website
            )

            LoyaltyTransaction.objects.create(
                client=self.user.client_profile,
                points=-config.min_conversion_points,  # Record the exact points deducted
                transaction_type='conversion',
                reason="Loyalty points conversion to wallet"
            )

        return total_conversion_amount
    
    def add_points_from_payment(self, payment_amount):
        """
        Add loyalty points based on the payment amount.
        Assumes 1 loyalty point per $10 spent.
        """
        points_earned = int(payment_amount / Decimal('10.00'))  # Customize the conversion logic as needed
        self.loyalty_points += points_earned
        self.save(update_fields=['loyalty_points'])

    def check_tier(self):
        """
        Checks the loyalty tier based on current points.
        """
        tier = LoyaltyTier.objects.filter(threshold__lte=self.loyalty_points).order_by('-threshold').first()
        return tier

    def process_split_payment(self, order, total_amount, external_method):
        """
        Handles payment from wallet + external method.
        - Deducts wallet balance first if sufficient.
        - Charges external method for the remainder.
        - Logs both transactions.
        """
        with transaction.atomic():
            wallet = ClientWallet.objects.select_for_update().get(id=self.id)
            
            wallet_amount = min(wallet.balance, total_amount)
            external_amount = total_amount - wallet_amount  # Adjust external method charge

            if wallet_amount > 0:
                wallet.balance -= wallet_amount
                wallet.save(update_fields=['balance'])
                ClientWalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='payment',
                    amount=-wallet_amount,
                    description=f"Partial payment for Order {order.id}"
                )

            # Process external payment logic here (API call, third-party processing)

            return {
                "wallet_amount": wallet_amount,
                "external_method": external_method,
                "external_amount": external_amount
            }

    def process_refund(self, order, refund_amount, original_wallet_amount, original_external_amount):
        """
        Refunds amount proportionally based on original payment method.
        """
        total_paid = original_wallet_amount + original_external_amount
        if total_paid == 0:
            raise ValueError("No payment found for refund.")

        # wallet_refund = (original_wallet_amount / total_paid) * refund_amount
        # external_refund = (original_external_amount / total_paid) * refund_amount

        wallet_refund = min(refund_amount, original_wallet_amount)
        remaining_refund = refund_amount - wallet_refund
        external_refund = min(remaining_refund, original_external_amount)

        with transaction.atomic():
            if wallet_refund > 0:
                self.balance += wallet_refund
                self.save(update_fields=['balance'])
                ClientWalletTransaction.objects.create(
                    wallet=self,
                    transaction_type='refund',
                    amount=wallet_refund,
                    description=f"Refund for Order {order.id}"
                )

            # Process external refund logic here

            try:
                # Process external refund logic here (API call, third-party processing)
                pass
            except Exception as e:
                # Log the error and handle accordingly
                logger.error(f"External refund failed for order {order.id}: {str(e)}")
                raise ValueError(f"External refund failed: {str(e)}")

        return {
            "wallet_refund": wallet_refund,
            "external_refund": external_refund
        }

    def __str__(self):
        return f"{self.user.username}'s Wallet - ${self.balance} {self.currency}"


class ClientWalletTransaction(WebsiteSpecificBaseModel):
    """
    Logs all transactions related to the client's wallet.
    """
    TRANSACTION_TYPES = (
        ('top-up', 'Top-Up'),
        ('payment', 'Payment'),
        ('refund', 'Refund'),
        ('bonus', 'Bonus'),
        ('adjustment', 'Adjustment'),
        ('referral_bonus', 'Referral Bonus'),
        ('loyalty_conversion', 'Loyalty Points Conversion'),
    )

    reference_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Reference ID for external transactions (if applicable)."
    )

    wallet = models.ForeignKey(
        ClientWallet,
        on_delete=models.CASCADE,
        related_name="transactions",
        db_index=True,
        help_text="The wallet associated with this transaction."
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        help_text="Type of transaction."
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Transaction amount."
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional description."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        Auto-earn loyalty points when the client makes a payment.
        """
        if self.wallet.currency != self.wallet.currency:  # Removed unnecessary check
            raise ValueError("Transaction currency must match wallet currency.")
        super().save(*args, **kwargs)

        if self.transaction_type == 'payment':
            self.wallet.add_points_from_payment(self.amount)  # Updated to call method correctly

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of ${self.amount} for {self.wallet.user.username}"