from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.conf import settings
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
        'websites.Website',
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
    website = models.ForeignKey(
        'websites.Website', 
        on_delete=models.CASCADE,
        related_name="loyalty_transactions_for_website"
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
    redemption_request = models.ForeignKey(
        'RedemptionRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
        help_text="Associated redemption request if this is a redemption transaction"
    )

    class Meta:
        verbose_name = _("Loyalty Transaction")
        verbose_name_plural = _("Loyalty Transactions")
        ordering = ['-timestamp']

    def __str__(self):
        return f"Transaction: {self.points} points ({self.transaction_type}) for {self.client.user.username}"

    def save(self, *args, **kwargs):
        if not getattr(self, 'website_id', None):
            try:
                if getattr(self, 'client', None) and getattr(self.client, 'website_id', None):
                    self.website_id = self.client.website_id
                else:
                    site = Website.objects.filter(is_active=True).first()
                    if site is None:
                        site = Website.objects.create(name="Test Website", domain="https://test.local", is_active=True)
                    self.website_id = site.id
            except Exception:
                pass
        super().save(*args, **kwargs)


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
    website = models.ForeignKey(
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
        help_text=_(
            "Loyalty points rewarded upon achieving this milestone."
            "Set to 0 for no reward."
        )
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
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="client_badges"
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
        unique_together = ('client', 'badge_name', 'website')

    def __str__(self):
        return f"Badge: {self.badge_name} for {self.client.user.username}"
    

class LoyaltyPointsConversionConfig(models.Model):
    """
    Configurations for converting loyalty points into wallet balance.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="loyalty_points_conversion_config"
    )
    points_per_dollar = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.1"),
        help_text="Number of loyalty points earned per dollar spent."
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


# ============================================================================
# LOYALTY POINTS REDEMPTION SYSTEM
# ============================================================================

class RedemptionCategory(models.Model):
    """
    Categories for redemption items (e.g., Discounts, Products, Services, Cash)
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="redemption_categories"
    )
    name = models.CharField(
        max_length=100,
        help_text="Category name (e.g., 'Discounts', 'Products', 'Services')"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this redemption category"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this category is active for redemptions"
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Display order for categories"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Redemption Category"
        verbose_name_plural = "Redemption Categories"
        ordering = ['sort_order', 'name']
        constraints = [
            models.UniqueConstraint(fields=['website', 'name'], name='unique_category_per_website')
        ]

    def __str__(self):
        return f"{self.name} ({self.website.name})"


class RedemptionItem(models.Model):
    """
    Items that clients can redeem using loyalty points.
    """
    REDEMPTION_TYPES = (
        ('discount', _('Discount Code')),
        ('cash', _('Cash/Wallet Credit')),
        ('product', _('Physical Product')),
        ('service', _('Service Credit')),
        ('voucher', _('Voucher/Code')),
    )
    
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="redemption_items"
    )
    category = models.ForeignKey(
        RedemptionCategory,
        on_delete=models.PROTECT,
        related_name="items",
        help_text="Category this redemption item belongs to"
    )
    name = models.CharField(
        max_length=200,
        help_text="Name of the redemption item (e.g., '$10 Discount', 'Free Writing Service')"
    )
    description = models.TextField(
        help_text="Detailed description of what the client receives"
    )
    points_required = models.PositiveIntegerField(
        help_text="Number of loyalty points required for redemption"
    )
    redemption_type = models.CharField(
        max_length=20,
        choices=REDEMPTION_TYPES,
        default='discount',
        help_text="Type of redemption item"
    )
    
    # Type-specific fields
    discount_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Discount code to generate/apply (for discount type)"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Discount amount in dollars (for discount/cash types)"
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Discount percentage (for discount type)"
    )
    
    # Inventory management
    stock_quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Available stock (None = unlimited)"
    )
    total_redemptions = models.PositiveIntegerField(
        default=0,
        help_text="Total number of times this item has been redeemed"
    )
    
    # Limits
    max_per_client = models.PositiveIntegerField(
        default=1,
        help_text="Maximum times a single client can redeem this item"
    )
    min_tier_level = models.ForeignKey(
        LoyaltyTier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="redemption_items_requiring_tier",
        help_text="Minimum loyalty tier required to redeem"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this item is available for redemption"
    )
    image_url = models.URLField(
        blank=True,
        null=True,
        help_text="Image URL for the redemption item"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Redemption Item"
        verbose_name_plural = "Redemption Items"
        ordering = ['category', 'points_required']

    def __str__(self):
        return f"{self.name} ({self.points_required} points)"

    def is_available(self):
        """Check if item is available for redemption"""
        if not self.is_active:
            return False
        if self.stock_quantity is not None and self.stock_quantity <= 0:
            return False
        return True

    def can_redeem(self, client_profile):
        """Check if a client can redeem this item"""
        if not self.is_available():
            return False, "Item is not available"
        
        if client_profile.loyalty_points < self.points_required:
            return False, f"Insufficient points. Required: {self.points_required}, Available: {client_profile.loyalty_points}"
        
        if self.min_tier_level:
            client_tier = client_profile.tier
            if not client_tier or client_tier.threshold < self.min_tier_level.threshold:
                return False, f"Requires {self.min_tier_level.name} tier or higher"
        
        # Check redemption limit per client
        client_redemptions = RedemptionRequest.objects.filter(
            item=self,
            client=client_profile,
            status='fulfilled'
        ).count()
        
        if client_redemptions >= self.max_per_client:
            return False, f"Maximum redemption limit ({self.max_per_client}) reached"
        
        return True, "Can redeem"


class RedemptionRequest(models.Model):
    """
    Tracks redemption requests from clients.
    """
    STATUS_CHOICES = (
        ('pending', _('Pending Approval')),
        ('approved', _('Approved')),
        ('fulfilled', _('Fulfilled')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled')),
    )
    
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="redemption_requests"
    )
    client = models.ForeignKey(
        'client_management.ClientProfile',
        on_delete=models.CASCADE,
        related_name="redemption_requests"
    )
    item = models.ForeignKey(
        RedemptionItem,
        on_delete=models.PROTECT,
        related_name="requests"
    )
    points_used = models.PositiveIntegerField(
        help_text="Points deducted for this redemption"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the redemption request"
    )
    
    # Fulfillment details
    fulfillment_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Generated code/voucher for fulfillment (e.g., discount code)"
    )
    fulfillment_details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional fulfillment details (e.g., tracking number, delivery address)"
    )
    
    # Admin tracking
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_redemptions",
        help_text="Admin who approved this redemption"
    )
    fulfilled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fulfilled_redemptions",
        help_text="Admin who fulfilled this redemption"
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for rejection if applicable"
    )
    
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Redemption Request"
        verbose_name_plural = "Redemption Requests"
        ordering = ['-requested_at']

    def __str__(self):
        return f"Redemption: {self.item.name} by {self.client.user.username} ({self.status})"


# ============================================================================
# ANALYTICS DASHBOARD MODELS
# ============================================================================

class LoyaltyAnalytics(models.Model):
    """
    Aggregated analytics data for loyalty program performance.
    Updated periodically via scheduled tasks.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="loyalty_analytics"
    )
    
    # Date range for this analytics snapshot
    date_from = models.DateField()
    date_to = models.DateField()
    
    # Overall metrics
    total_active_clients = models.PositiveIntegerField(
        default=0,
        help_text="Total clients with loyalty points"
    )
    total_points_issued = models.PositiveIntegerField(
        default=0,
        help_text="Total points issued in period"
    )
    total_points_redeemed = models.PositiveIntegerField(
        default=0,
        help_text="Total points redeemed in period"
    )
    total_points_balance = models.PositiveIntegerField(
        default=0,
        help_text="Total outstanding points balance"
    )
    
    # Redemption metrics
    total_redemptions = models.PositiveIntegerField(
        default=0,
        help_text="Total number of redemptions"
    )
    total_redemption_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.0,
        help_text="Total value of redemptions (in points)"
    )
    most_popular_item = models.ForeignKey(
        RedemptionItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analytics_as_popular"
    )
    
    # Tier distribution
    bronze_count = models.PositiveIntegerField(default=0)
    silver_count = models.PositiveIntegerField(default=0)
    gold_count = models.PositiveIntegerField(default=0)
    platinum_count = models.PositiveIntegerField(default=0)
    
    # Engagement metrics
    active_redemptions_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        help_text="Percentage of active clients who redeemed"
    )
    average_points_per_client = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0
    )
    
    # Timestamps
    calculated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Loyalty Analytics"
        verbose_name_plural = "Loyalty Analytics"
        constraints = [
            models.UniqueConstraint(fields=['website', 'date_from', 'date_to'], name='unique_analytics_per_website_date_range')
        ]
        ordering = ['-date_to', '-date_from']

    def __str__(self):
        return f"Analytics: {self.website.name} ({self.date_from} to {self.date_to})"


class DashboardWidget(models.Model):
    """
    Configurable widgets for the analytics dashboard.
    """
    WIDGET_TYPES = (
        ('points_issued', 'Points Issued Over Time'),
        ('redemptions_trend', 'Redemptions Trend'),
        ('tier_distribution', 'Loyalty Tier Distribution'),
        ('top_redemptions', 'Top Redemption Items'),
        ('engagement_rate', 'Client Engagement Rate'),
        ('points_balance', 'Total Points Balance'),
        ('conversion_rate', 'Points to Wallet Conversion'),
    )
    
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="dashboard_widgets"
    )
    widget_type = models.CharField(
        max_length=50,
        choices=WIDGET_TYPES,
        help_text="Type of widget to display"
    )
    title = models.CharField(
        max_length=200,
        help_text="Widget title"
    )
    position = models.PositiveIntegerField(
        default=0,
        help_text="Display position on dashboard"
    )
    is_visible = models.BooleanField(
        default=True,
        help_text="Whether widget is visible"
    )
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Widget configuration (chart type, date range, etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dashboard Widget"
        verbose_name_plural = "Dashboard Widgets"
        ordering = ['position', 'title']

    def __str__(self):
        return f"{self.title} ({self.website.name})"
