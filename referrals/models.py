from django.db import models, transaction
from django.utils.timezone import now
from django.conf import settings
from decimal import Decimal
import uuid

from users.models import User
from wallet.models import Wallet, WalletTransaction
from websites.models import Website
from loyalty_management.models import LoyaltyTransaction, LoyaltyTier
from django.apps import apps

def get_order_payment_model():
    return apps.get_model('order_payments_management', 'OrderPayment')
class SoftDeleteModel(models.Model):
    """Abstract model for soft deletion instead of permanent deletion."""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        """Marks an object as deleted without removing it from the database."""
        self.is_deleted = True
        self.deleted_at = now()
        self.save()

    class Meta:
        abstract = True

class ReferralBonusManager(models.Manager):
    def active(self):
        return self.filter(is_deleted=False)

    def expired(self):
        return self.filter(is_deleted=True)

class Referral(SoftDeleteModel):
    """
    Tracks referrals and ensures bonuses are awarded only after the referee orders.
    """
    objects = ReferralBonusManager()
    referrer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="referrals",
        help_text="The user who made the referral."
    )
    website = models.ForeignKey(Website, on_delete=models.CASCADE) 
    referee = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="referred_by",
        help_text="The user who was referred."
    )
    referral_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Unique referral code used by the referee."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    bonus_awarded = models.BooleanField(default=False)
    registration_bonus_credited = models.BooleanField(default=False)
    first_order_bonus_credited = models.BooleanField(default=False)

    def award_bonus(self):
        """Credits the referral bonus when the referee places their first paid and completed order."""
        if self.bonus_awarded:
            return  # Avoid duplicate bonuses

        bonus_config = ReferralBonusConfig.objects.filter(website=self.website).first()
        if not bonus_config:
            return  # No bonus config set up

        # Check if the referee has placed a paid and completed order
        first_paid_order = self.referee.orders.filter(status='completed', payment_status='paid').first()
        
        if not first_paid_order:
            return  # No paid and completed order found, so don't award bonus

        referrer_wallet = Wallet.objects.get(user=self.referrer)

        with transaction.atomic():
            # Award referral bonus
            WalletTransaction.objects.create(
                wallet=referrer_wallet,
                transaction_type='bonus',
                amount=bonus_config.first_order_bonus,
                description="Referral Bonus",
                website=self.website,
            )

            # Award loyalty points
            LoyaltyTransaction.objects.create(
                client=self.referrer.client_profile,
                points=bonus_config.first_order_bonus * 10,  # Example: 10 points per $1 bonus
                transaction_type='add',
                reason="Referral Bonus Earned",
            )

            self.bonus_awarded = True
            self.save()


    def apply_referral_discount(self, order):
        """
        Applies referral discount for the referee when it's their first order.
        This function is placed inside the Referral model.
        """
        # Check if it's client's first order
        if order.user.orders.count() == 1:  # The referee is placing their first order
            # Check if the order is linked to the current referral
            if self.referred_user == order.user:
                # Get referral bonus configuration for the current website
                bonus_config = ReferralBonusConfig.objects.filter(website=self.website).first()
                if bonus_config:
                    # Apply the discount based on the bonus configuration
                    discount_amount = 0
                    if bonus_config.first_order_discount_type == 'percentage':
                        discount_amount = (bonus_config.first_order_discount_amount / 100) * order.total  # Apply percentage
                    elif bonus_config.first_order_discount_type == 'fixed':
                        discount_amount = bonus_config.first_order_discount_amount  # Apply fixed amount

                    # Deduct the discount from the order total
                    order.total -= discount_amount
                    order.save()

                    # Optionally create a wallet transaction for the referrer
                    self._create_wallet_transaction(order, discount_amount)
                    
                    # Mark the referral as bonus credited
                    self.first_order_referral_bonus_credited = True
                    self.save()

                    return discount_amount
        return 0  # No discount if conditions aren't met

    def _create_wallet_transaction(self, order, discount_amount):
        """Creates a wallet transaction for the referrer when the discount is applied."""
        # Create wallet transaction for the referrer
        wallet, created = Wallet.objects.get_or_create(user=self.referrer)
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='referral_bonus',
            amount=discount_amount,
            description=f"Referral Bonus: First Order Discount for {order.user.username}",
            website=self.website,
        )

    def __str__(self):
        return f"{self.referrer.username} referred {self.referee.username}"


class ReferralBonusConfig(models.Model):
    """
    Configures referral bonuses and limits per website.
    """
    website = models.ForeignKey(Website, on_delete=models.CASCADE) 
    first_order_bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        help_text="Bonus amount when a referee places their first order."
    )
    first_order_discount_type = models.CharField(
        max_length=10, choices=[('percentage', 'Percentage'), ('fixed', 'Fixed')], default='fixed'
    )  # To define if the discount is percentage or fixed amount
    first_order_discount_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Discount value
    bonus_expiry_days = models.IntegerField(default=30) 
    max_referrals_per_month = models.PositiveIntegerField(
        default=10,
        help_text="Max number of referrals a user can make in a month."
    )
    max_referral_bonus_per_month = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=100.0,
        help_text="Max referral bonus a user can earn in a month."
    )

    def __str__(self):
        return f"Referral Bonus Config for {self.website.name}"


class ReferralCode(models.Model):
    """
    Stores referral codes and generates unique referral links.
    """
    website = models.ForeignKey(Website, on_delete=models.CASCADE) 
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="referral_code",
        help_text="The user associated with this referral code."
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique referral code."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def get_referral_link(self):
        """Dynamically generates a referral link."""
        return f"https://{self.website.domain}/order?ref={self.code}"

    @staticmethod
    def generate_unique_code(user, website):
        """Generates a unique referral code."""
        return f"REF-{user.id}-{uuid.uuid4().hex[:6].upper()}"

    def __str__(self):
        return f"Referral Code: {self.code} (User: {self.user.username})"


class ReferralStats(models.Model):
    """
    Tracks referral statistics for each user.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="referral_stats",
        help_text="The user whose referral stats are tracked."
    )
    total_referrals = models.PositiveIntegerField(default=0)
    successful_referrals = models.PositiveIntegerField(default=0)
    referral_bonus_earned = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0
    )
    last_referral_at = models.DateTimeField(null=True, blank=True)

    def update_stats(self, bonus_amount, successful):
        """Updates referral stats when a bonus is awarded."""
        self.total_referrals += 1
        if successful:
            self.successful_referrals += 1
            self.referral_bonus_earned += bonus_amount
        self.last_referral_at = now()
        self.save()

    def __str__(self):
        return f"{self.user.username} Referral Stats"


class ReferralBonusDecay(models.Model):
    """
    Implements bonus decay instead of expiration.
    """
    wallet_transaction = models.OneToOneField(
        WalletTransaction,
        on_delete=models.CASCADE,
        related_name="decay",
        help_text="The wallet transaction associated with the bonus."
    )
    decay_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.0,
        help_text="Decay percentage per month."
    )
    decay_start_at = models.DateTimeField(
        help_text="When the decay starts applying."
    )

    def apply_decay(self):
        """Applies decay to the bonus."""
        months_since = (now().year - self.decay_start_at.year) * 12 + \
                       (now().month - self.decay_start_at.month)
        if months_since > 0:
            decay_multiplier = Decimal((100 - self.decay_rate) / 100) ** months_since
            new_amount = self.wallet_transaction.amount * decay_multiplier
            self.wallet_transaction.amount = new_amount
            self.wallet_transaction.save()

    def __str__(self):
        return f"Decay for {self.wallet_transaction.id}: {self.decay_rate}%/month"
    

class ReferralBonusUsage(models.Model):
    """
    Tracks the usage of a referral bonus.
    """
    referral = models.ForeignKey(Referral, on_delete=models.CASCADE)
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE)
    payment = models.ForeignKey('order_payments_management.OrderPayment', on_delete=models.CASCADE)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Referral bonus of {self.discount_amount} applied to Order {self.order.id} (Payment {self.payment.transaction_id})"