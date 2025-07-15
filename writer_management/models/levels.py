from django.db import models
from websites.models import Website
from writer_management.models.profile import WriterProfile
from django.contrib.auth import get_user_model

User = get_user_model()



class WriterLevel(models.Model):
    """
    Represents different levels or tiers of writers.
    Includes base pay rates, urgent order multipliers, and technical order adjustments.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_level"
    )
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Name of the writer level (e.g., Beginner, Intermediate)."
    )
    max_orders = models.PositiveIntegerField(
        default=10,
        help_text="Maximum number of orders the writer can take simultaneously."
    )
    
    # Base pay rates
    base_pay_per_page = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Base pay per page."
    )
    base_pay_per_slide = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Base pay per slide."
    )

    # Urgency-based multipliers
    urgency_percentage_increase = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        help_text="Percentage increase for urgent orders."
    )
    urgency_deadline_limit = models.PositiveIntegerField(
        default=8,
        help_text="Maximum hours considered as 'urgent' (e.g., orders within 8 hours get extra pay)."
    )

    # Technical order adjustments
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

    tip_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        help_text="Tip percentage."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Writer Level"
        verbose_name_plural = "Writer Levels"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (Max Orders: {self.max_orders}, Base Pay/Page: {self.base_pay_per_page})"

    def calculate_order_payment(self, pages, slides, is_urgent, is_technical):
        """
        Calculate the writer's earnings based on the order details.
        """
        base_payment = (pages * self.base_pay_per_page) + (slides * self.base_pay_per_slide)

        # Apply urgency adjustment if the order is urgent
        if is_urgent:
            base_payment += (base_payment * (self.urgency_percentage_increase / 100))

        # Apply technical order adjustments
        if is_technical:
            base_payment += (pages * self.technical_order_adjustment_per_page) + (slides * self.technical_order_adjustment_per_slide)

        return round(base_payment, 2)
    
    def full_payout(self, pages, slides, is_urgent, is_technical):
        """Calculate the full payout including tips."""
        base = self.calculate_order_payment(pages, slides, is_urgent, is_technical)
        tip = base * (self.tip_percentage / 100)
        return round(base + tip, 2)


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