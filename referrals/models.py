from django.db import models, transaction
from django.utils.timezone import now
from django.conf import settings
from decimal import Decimal
import uuid
from wallet.models import Wallet, WalletTransaction
from websites.models import Website
from loyalty_management.models import LoyaltyTransaction, LoyaltyTier
from django.apps import apps

User = settings.AUTH_USER_MODEL 

def get_order_payment_model():
    return apps.get_model('order_payments_management', 'OrderPayment')
class SoftDeleteModel(models.Model):
    """Abstract model for soft deletion instead of permanent deletion."""
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='soft_deleted'
    )
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
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='referral'
    )
    objects = ReferralBonusManager()
    referrer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="referrals",
        help_text="The user who made the referral."
    )
    referee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="referrals_received",
        help_text="User who was referred."
    )
    referral_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Unique referral code used by the referee."
    )
    referral_source = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text="Optional: how the referral came in (manual, auto, promo code, etc)"
    )

    referrer_ip = models.GenericIPAddressField(null=True, blank=True)
    referee_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    bonus_awarded = models.BooleanField(default=False)
    registration_bonus_credited = models.BooleanField(default=False)
    first_order_bonus_credited = models.BooleanField(default=False)

    


    def apply_referral_discount(self, order):
        """
        Applies referral discount for the referee when it's their first order.
        This function is placed inside the Referral model.
        """
        # Check if it's client's first order
        # Order model uses 'client' field for the client who placed the order
        order_client = getattr(order, 'client', None) or getattr(order, 'user', None)
        if not order_client:
            return 0
        
        if order_client.orders_as_client.count() == 1:  # The referee is placing their first order
            # Check if the order is linked to the current referral
            if self.referee == order_client:
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

                    # Mark the referral as bonus credited
                    self.first_order_referral_bonus_credited = True
                    self.save()

                    return discount_amount
        return 0  # No discount if conditions aren't met

    

    def __str__(self):
        return f"{self.referrer.username} referred {self.referee.username}"

    def save(self, *args, **kwargs):
        if not getattr(self, "website_id", None):
            try:
                if getattr(self.referrer, "website_id", None):
                    self.website_id = self.referrer.website_id
                elif getattr(self.referee, "website_id", None):
                    self.website_id = self.referee.website_id
                else:
                    site = Website.objects.filter(is_active=True).first()
                    if site is None:
                        site = Website.objects.create(name="Test Website", domain="https://test.local", is_active=True)
                    self.website_id = site.id
            except Exception:
                pass
        super().save(*args, **kwargs)


class ReferralBonusConfig(models.Model):
    """
    Configures referral bonuses and limits per website.
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed')
    ]
    website = models.ForeignKey(Website, on_delete=models.CASCADE) 
    first_order_bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        help_text="Bonus amount when a referee places their first order."
    )
    first_order_discount_type = models.CharField(
        max_length=10,  choices=DISCOUNT_TYPE_CHOICES,
        default='fixed'
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

    def __str__(self):
        return f"Referral Code: {self.code} (User: {self.user.username})"

    def get_referral_link(self):
        """Generate referral link for this code."""
        # Link should point to signup/registration page with referral code
        domain = self.website.domain.replace('https://', '').replace('http://', '')
        return f"https://{domain}/signup?ref={self.code}"

    def save(self, *args, **kwargs):
        if not getattr(self, "website_id", None):
            try:
                if getattr(self.user, "website_id", None):
                    self.website_id = self.user.website_id
                else:
                    site = Website.objects.filter(is_active=True).first()
                    if site is None:
                        site = Website.objects.create(name="Test Website", domain="https://test.local", is_active=True)
                    self.website_id = site.id
            except Exception:
                pass
        super().save(*args, **kwargs)


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



    def __str__(self):
        return f"{self.user.username} Referral Stats"


class ReferralBonusDecay(models.Model):
    """
    Implements bonus decay instead of expiration.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='referral_bonus_decay'
    )
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
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='referral_bonus_usage'
    )
    referral = models.ForeignKey(
        Referral,
        on_delete=models.CASCADE
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE
    )
    payment = models.ForeignKey(
        'order_payments_management.OrderPayment',
        on_delete=models.CASCADE
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Referral bonus of {self.discount_amount} applied to Order {self.order.id} (Payment {self.payment.transaction_id})"


class PendingReferralInvitation(models.Model):
    """
    Tracks referral invitations sent to people who don't have accounts yet.
    When they sign up using the referral code, this will be converted to a Referral.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='pending_referral_invitations'
    )
    referrer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pending_referral_invitations",
        help_text="The user who sent the referral invitation."
    )
    referee_email = models.EmailField(
        help_text="Email address of the person being referred (they don't have an account yet)."
    )
    referral_code = models.CharField(
        max_length=50,
        help_text="Referral code to be used when they sign up."
    )
    referral_link = models.URLField(
        help_text="Full referral link sent to the referee."
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    invitation_sent = models.BooleanField(default=False)
    converted = models.BooleanField(
        default=False,
        help_text="True when the invitation has been converted to a Referral (user signed up)."
    )
    converted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['referrer', 'referee_email', 'website']
        indexes = [
            models.Index(fields=['referee_email', 'website']),
            models.Index(fields=['referral_code']),
        ]

    def __str__(self):
        return f"Invitation from {self.referrer.username} to {self.referee_email}"

    def mark_as_converted(self):
        """Mark this invitation as converted when the user signs up."""
        self.converted = True
        self.converted_at = now()
        self.save()