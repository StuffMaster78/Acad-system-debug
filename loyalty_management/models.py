from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from websites.models import Website
from django.apps import apps
from decimal import Decimal
# from core.models.base import WebsiteSpecificBaseModel

class LoyaltyTier(models.Model):
    """
    Represents a loyalty tier for clients.
    Clients are assigned to tiers based on their accumulated loyalty points.
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Name of the loyalty tier (e.g., Bronze, Silver, Gold).")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="loyalty_tiers",
        help_text=_("Website this tier is associated with."),
    )
    threshold = models.PositiveIntegerField(
        help_text=_("Minimum points required to qualify for this tier.")
    )
    discount_percentage = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.0,
        help_text=_("Discount percentage for clients in this tier.")
    )
    perks = models.TextField(
        blank=True,
        null=True,
        help_text=_("Additional perks or benefits for this tier.")
    )

    class Meta:
        verbose_name = _("Loyalty Tier")
        verbose_name_plural = _("Loyalty Tiers")
        ordering = ['threshold']

    def __str__(self):
        return f"{self.name} (Min Threshold: {self.threshold} points)"


class LoyaltyTransaction(models.Model):
    """
    Tracks loyalty point transactions for clients.
    """
    TRANSACTION_TYPES = (
        ('add', _('Add')),
        ('redeem', _('Redeem')),
        ('deduct', _('Deduct')),
    )
    website = models.OneToOneField(
        'websites.Website', 
        on_delete=models.CASCADE,
        related_name="loyalty_transactions"
    )

    client = models.ForeignKey(
        'client_management.ClientProfile',
        on_delete=models.CASCADE,
        related_name="loyalty_transactions",
        help_text=_("Client associated with this transaction.")
    )
    points = models.IntegerField(
        help_text=_("Number of points added, redeemed, or deducted.")
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        default='add',
        help_text=_("Type of transaction (add, redeem, deduct).")
    )
    reason = models.TextField(
        blank=True,
        null=True,
        help_text=_("Reason for the loyalty transaction.")
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Time when the transaction was recorded.")
    )

    class Meta:
        verbose_name = _("Loyalty Transaction")
        verbose_name_plural = _("Loyalty Transactions")
        ordering = ['-timestamp']

    def __str__(self):
        return f"Transaction: {self.points} points ({self.transaction_type}) for {self.client.user.username}"


class Milestone(models.Model):
    """
    Represents a milestone that clients can achieve.
    Milestones reward clients with loyalty points upon completion.
    """
    TARGET_TYPES = (
        ('total_spent', _('Total Spent')),
        ('loyalty_points', _('Loyalty Points')),
        ('orders_placed', _('Orders Placed')),
    )
    website = models.OneToOneField(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="milestone_achieveable"
    )

    name = models.CharField(
        max_length=100,
        help_text=_("Name of the milestone (e.g., 'First $100 Spent').")
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text=_("Details about the milestone.")
    )
    target_type = models.CharField(
        max_length=50,
        choices=TARGET_TYPES,
        help_text=_("Type of milestone (e.g., total spent, loyalty points).")
    )
    target_value = models.PositiveIntegerField(
        help_text=_("Value the client must achieve to earn this milestone.")
    )
    reward_points = models.PositiveIntegerField(
        default=0,
        help_text=_("Loyalty points rewarded upon achieving this milestone.")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this milestone was created.")
    )

    class Meta:
        verbose_name = _("Milestone")
        verbose_name_plural = _("Milestones")
        ordering = ['target_value']

    def __str__(self):
        return f"Milestone: {self.name} (Target: {self.target_value})"


class ClientBadge(models.Model):
    """
    Represents badges awarded to clients for specific achievements.
    """
    website = models.OneToOneField(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="client_badge"
    )
    client = models.ForeignKey(
        'client_management.ClientProfile',
        on_delete=models.CASCADE,
        related_name="badges",
        help_text=_("Client who earned this badge.")
    )
    badge_name = models.CharField(
        max_length=100,
        help_text=_("Name of the badge (e.g., 'Top Spender').")
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text=_("Details about why this badge was awarded.")
    )
    awarded_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this badge was awarded.")
    )

    class Meta:
        verbose_name = _("Client Badge")
        verbose_name_plural = _("Client Badges")

    def __str__(self):
        return f"Badge: {self.badge_name} for {self.client.user.username}"
    

class LoyaltyPointsConversionConfig(models.Model):
    """
    Configurations for converting loyalty points into wallet balance.
    """
    website = models.OneToOneField(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="loyalty_points_conversion_config"
    )
    conversion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal('0.10'),
        help_text="Rate at which loyalty points are converted to wallet balance."
    )
    min_conversion_points = models.PositiveIntegerField(
        default=100,
        help_text="Minimum number of points required for conversion."
    )
    max_conversion_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('500.00'),
        help_text="Maximum limit for conversion in wallet balance."
    )
    active = models.BooleanField(
        default=True,
        help_text="Indicates whether loyalty points conversion is currently enabled."
    )

    def __str__(self):
        return f"Loyalty Points Conversion Config for {self.website.name}"