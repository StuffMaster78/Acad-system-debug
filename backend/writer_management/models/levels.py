from django.db import models
from decimal import Decimal
from websites.models import Website
from writer_management.models.profile import WriterProfile
from django.contrib.auth import get_user_model

User = get_user_model()



class WriterLevel(models.Model):
    """
    Represents different levels or tiers of writers.
    Includes base pay rates, urgent order multipliers, technical order adjustments,
    and comprehensive earning models (fixed or percentage-based).
    """
    # EARNING CALCULATION MODE
    EARNING_MODE_CHOICES = [
        ('fixed_per_page', 'Fixed Per Page/Slide'),
        ('percentage_of_order_cost', 'Percentage of Order Cost'),
        ('percentage_of_order_total', 'Percentage of Order Total'),
    ]
    
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_level_definitions"
    )
    name = models.CharField(
        max_length=50,
        help_text="Name of the writer level (e.g., Novice, Intermediate, Expert)."
    )
    description = models.TextField(
        blank=True,
        help_text="Description of this level and its benefits."
    )
    
    # EARNING MODE
    earning_mode = models.CharField(
        max_length=30,
        choices=EARNING_MODE_CHOICES,
        default='fixed_per_page',
        help_text="How writer earnings are calculated"
    )
    
    # BASE PAY RATES (for fixed_per_page mode)
    base_pay_per_page = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Base pay per page (used in fixed_per_page mode or as minimum fallback)."
    )
    base_pay_per_slide = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Base pay per slide (used in fixed_per_page mode or as minimum fallback)."
    )
    
    # PERCENTAGE-BASED EARNINGS (when earning_mode is percentage)
    earnings_percentage_of_cost = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        help_text="Percentage of order cost (before discounts) writer earns"
    )
    earnings_percentage_of_total = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        help_text="Percentage of order total (after discounts) writer earns"
    )

    # URGENCY-BASED MULTIPLIERS
    urgency_percentage_increase = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        help_text="Percentage increase for urgent orders."
    )
    urgency_additional_per_page = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="Additional amount per page for urgent orders (beyond percentage increase)"
    )
    urgency_deadline_limit = models.PositiveIntegerField(
        default=8,
        help_text="Maximum hours considered as 'urgent' (e.g., orders within 8 hours get extra pay)."
    )
    urgent_order_deadline_hours = models.PositiveIntegerField(
        default=8,
        help_text="Hours before deadline that order is considered urgent for this level"
    )

    # TECHNICAL ORDER ADJUSTMENTS
    technical_order_adjustment_per_page = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Extra pay per page for technical orders."
    )
    technical_order_adjustment_per_slide = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="Extra pay per slide for technical orders."
    )

    # DEADLINE MANAGEMENT
    deadline_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=80.00,
        help_text="Percentage of client deadline writer receives (e.g., 80% means writer gets 80% of client deadline time)"
    )

    # TIPS & BONUSES
    tip_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=100.00,
        help_text="Percentage of tips writer receives (100% = full tips, 50% = half tips)"
    )
    tips_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=100.00,
        help_text="Percentage of tips writer receives (alias for tip_percentage)"
    )
    
    # LEVEL PROGRESSION REQUIREMENTS
    min_orders_to_attain = models.PositiveIntegerField(
        default=0,
        help_text="Minimum number of completed orders required to reach this level"
    )
    min_rating_to_attain = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00,
        help_text="Minimum average rating required to reach this level"
    )
    min_takes_to_attain = models.PositiveIntegerField(
        default=0,
        help_text="Minimum number of successful order takes required to reach this level"
    )
    min_completion_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        help_text="Minimum order completion rate (%) required"
    )
    max_revision_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Maximum acceptable revision rate (%) for this level"
    )
    max_lateness_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Maximum acceptable lateness rate (%) for this level"
    )
    
    # BONUS STRUCTURE
    bonus_per_order_completed = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="Fixed bonus per completed order"
    )
    bonus_per_rating_above_threshold = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="Bonus for orders rated above threshold (e.g., 4.5+)"
    )
    rating_threshold_for_bonus = models.DecimalField(
        max_digits=3, decimal_places=2, default=4.50,
        help_text="Rating threshold to qualify for bonus"
    )
    
    # LEVEL METADATA
    max_orders = models.PositiveIntegerField(
        default=10,
        help_text="Maximum number of orders the writer can take simultaneously (max_takes_per_writer)."
    )
    max_requests_per_writer = models.PositiveIntegerField(
        default=5,
        help_text="Maximum number of order requests a writer can have at once."
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Display order (lower = higher level, used for sorting)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this level is active and can be assigned"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Writer Level"
        verbose_name_plural = "Writer Levels"
        ordering = ['display_order', 'name']
        unique_together = [['website', 'name']]  # Level names unique per website

    def __str__(self):
        earning_display = f"${self.base_pay_per_page}/page" if self.earning_mode == 'fixed_per_page' else f"{self.earnings_percentage_of_cost or self.earnings_percentage_of_total}%"
        return f"{self.name} ({earning_display}, Max Orders: {self.max_orders})"

    def calculate_order_payment(self, pages, slides, is_urgent, is_technical, order_total=None, order_cost=None):
        """
        Calculate the writer's earnings based on the order details.
        This method is kept for backward compatibility but delegates to the new calculator.
        """
        from writer_management.services.earnings_calculator import WriterEarningsCalculator
        
        # Create a mock order object for compatibility
        class MockOrder:
            def __init__(self, pages, slides, total_price, discounted_amount=None):
                self.number_of_pages = pages
                self.number_of_slides = slides
                self.total_price = total_price
                self.discounted_amount = discounted_amount or total_price
        
        mock_order = MockOrder(pages, slides, order_total or Decimal('0.00'), order_cost)
        return WriterEarningsCalculator.calculate_earnings(
            self, mock_order, is_urgent, is_technical
        )
    
    def full_payout(self, pages, slides, is_urgent, is_technical, order_total=None, order_cost=None):
        """Calculate the full payout including tips."""
        base = self.calculate_order_payment(pages, slides, is_urgent, is_technical, order_total, order_cost)
        tip = base * (self.tip_percentage / 100)
        return round(base + tip, 2)

    def save(self, *args, **kwargs):
        # Ensure a website is always assigned during tests
        if not getattr(self, 'website_id', None):
            try:
                site = Website.objects.filter(is_active=True).first()
                if site is None:
                    site = Website.objects.create(name="Test Website", domain="https://test.local", is_active=True)
                self.website_id = site.id
            except Exception:
                pass
        super().save(*args, **kwargs)


class WriterLevelHistory(models.Model):
    """Tracks changes to a writer's level over time."""
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="level_history"
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    level = models.CharField(max_length=50)
    changed_at = models.DateTimeField(auto_now_add=True)
    triggered_by = models.CharField(
        max_length=50, default="system"
    )  # or "admin", "weekly_task", etc.

    class Meta:
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.writer.user.username} @ {self.level}"