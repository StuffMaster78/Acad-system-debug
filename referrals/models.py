from django.db import models
from django.utils.timezone import now
from django.db import transaction
from django.conf import settings
from users.models import User
from wallet.models import Wallet
import uuid

class SoftDeleteModel(models.Model):
    """Abstract model for soft deletion."""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = now()
        self.save()

    class Meta:
        abstract = True
class Referral(SoftDeleteModel):
    """
    Tracks referrals between users.
    """
    referrer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="referrals",
        help_text="The user who referred someone else."
    )
    website = models.CharField(max_length=255)
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
    registration_bonus_credited = models.BooleanField(
        default=False,
        help_text="Has the registration bonus been credited?"
    )
    first_order_bonus_credited = models.BooleanField(
        default=False,
        help_text="Has the first-order bonus been credited?"
    )

    def credit_bonus(self, bonus_amount):
        from wallet.models import Wallet, WalletTransaction  # Avoid circular import
        wallet = Wallet.objects.get(user=self.referrer)
        
        with transaction.atomic():
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='bonus',
                amount=bonus_amount,
                description="Referral Bonus",
                website=self.website,
            )
            self.registration_bonus_credited = True
            self.save()

    def __str__(self):
        return f"{self.referrer.username} referred {self.referee.username}"


class ReferralBonusConfig(models.Model):
    """
    Configures referral bonus rules.
    """
    website = models.CharField(max_length=255)
    registration_bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        help_text="Bonus amount for successful referee registration."
    )
    first_order_bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        help_text="Bonus amount for referee's first order."
    )
    referee_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        help_text="Discount for the referee's first order."
    )

    def __str__(self):
        return f"Referral Bonus Config for {self.website.name}"


class ReferralCode(models.Model):
    """
    Stores referral codes for users and generates referral links.
    """
    website = models.CharField(max_length=255)
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
        """Dynamically generate the referral link based on the website."""
        return f"https://{self.website}/order?ref={self.code}"
    @staticmethod
    def generate_unique_code(user, website):
        return f"REF-{user.id}-{uuid.uuid4().hex[:6].upper()}"

    def __str__(self):
        return f"Referral Code: {self.code} (User: {self.user.username})"