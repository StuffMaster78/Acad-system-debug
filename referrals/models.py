from django.db import models
from django.utils.timezone import now
from core.models.base import WebsiteSpecificBaseModel
from users.models import User
from wallet.models import Wallet


class Referral(WebsiteSpecificBaseModel):
    """
    Tracks referrals between users.
    """
    referrer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="referrals",
        help_text="The user who referred someone else."
    )
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

    def __str__(self):
        return f"{self.referrer.username} referred {self.referee.username}"


class ReferralBonusConfig(WebsiteSpecificBaseModel):
    """
    Configures referral bonus rules.
    """
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


class ReferralCode(WebsiteSpecificBaseModel):
    """
    Stores referral codes for users.
    """
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