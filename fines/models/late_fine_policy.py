"""
Extended FinePolicy model for progressive hourly lateness fines.
"""

from django.db import models
from django.utils import timezone
from decimal import Decimal
from websites.models import Website


class LatenessFineRule(models.Model):
    """
    Defines progressive fine rules for late submissions.
    Supports per-hour percentage increments (e.g., 5% first hour, 10% second hour, etc.)
    """
    
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='lateness_fine_rules',
        help_text="Website this rule applies to"
    )
    
    # Progressive hourly percentages
    first_hour_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('5.00'),
        help_text="Fine percentage for first hour late (e.g., 5%)"
    )
    
    second_hour_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('10.00'),
        help_text="Fine percentage for second hour late (e.g., 10%)"
    )
    
    third_hour_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('15.00'),
        help_text="Fine percentage for third hour late (e.g., 15%)"
    )
    
    # For hours 4-24, use a formula or fixed rate
    subsequent_hours_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('5.00'),
        help_text="Additional percentage per hour after 3 hours (e.g., 5% per hour)"
    )
    
    # Daily rate after 24 hours
    daily_rate_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('20.00'),
        help_text="Fine percentage per day after 24 hours (e.g., 20% per day)"
    )
    
    # Maximum fine cap
    max_fine_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum fine percentage cap (None = no cap)"
    )
    
    # Calculation mode
    CALCULATION_MODE_CHOICES = [
        ('cumulative', 'Cumulative (5% + 10% + 15% = 30% after 3 hours)'),
        ('progressive', 'Progressive (5% for hour 1, 10% for hour 2, 15% for hour 3, etc.)'),
    ]
    
    calculation_mode = models.CharField(
        max_length=20,
        choices=CALCULATION_MODE_CHOICES,
        default='cumulative',
        help_text="How to calculate fines: cumulative or progressive per hour"
    )
    
    # Base amount for calculation
    BASE_AMOUNT_CHOICES = [
        ('writer_compensation', 'Writer Compensation'),
        ('total_price', 'Order Total Price'),
    ]
    
    base_amount = models.CharField(
        max_length=20,
        choices=BASE_AMOUNT_CHOICES,
        default='writer_compensation',
        help_text="What amount to calculate fine percentage from"
    )
    
    active = models.BooleanField(
        default=True,
        help_text="Whether this rule is currently active"
    )
    
    start_date = models.DateTimeField(
        default=timezone.now,
        help_text="When this rule becomes active"
    )
    
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this rule expires (None = never expires)"
    )
    
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_lateness_rules',
        help_text="Admin who created this rule"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Admin notes about this rule"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Lateness Fine Rule"
        verbose_name_plural = "Lateness Fine Rules"
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['website', 'active']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"Lateness Fine Rule for {self.website.domain} ({self.calculation_mode})"
    
    def is_active(self):
        """Check if rule is currently active."""
        now = timezone.now()
        if not self.active:
            return False
        if self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True
    
    def calculate_fine(self, hours_late: float, base_amount: Decimal) -> Decimal:
        """
        Calculate fine amount based on hours late.
        
        Args:
            hours_late: Number of hours late (can be fractional)
            base_amount: Base amount to calculate percentage from
            
        Returns:
            Decimal: Fine amount
        """
        from decimal import ROUND_HALF_UP
        
        if hours_late <= 0:
            return Decimal('0.00')
        
        if self.calculation_mode == 'cumulative':
            # Cumulative: 5% + 10% + 15% + ...
            total_percentage = Decimal('0.00')
            
            # First hour
            if hours_late >= 1:
                total_percentage += self.first_hour_percentage
            
            # Second hour
            if hours_late >= 2:
                total_percentage += self.second_hour_percentage
            
            # Third hour
            if hours_late >= 3:
                total_percentage += self.third_hour_percentage
            
            # Hours 4-24
            if hours_late > 3:
                additional_hours = min(int(hours_late - 3), 21)  # Up to hour 24
                total_percentage += self.subsequent_hours_percentage * Decimal(str(additional_hours))
            
            # Daily rate after 24 hours
            if hours_late >= 24:
                days_late = int((hours_late - 24) / 24) + 1
                total_percentage += self.daily_rate_percentage * Decimal(str(days_late))
        
        else:  # progressive
            # Progressive: Use the percentage for the hour range we're in
            if hours_late < 1:
                total_percentage = Decimal('0.00')
            elif hours_late < 2:
                total_percentage = self.first_hour_percentage
            elif hours_late < 3:
                total_percentage = self.second_hour_percentage
            elif hours_late < 24:
                hour_number = int(hours_late)
                if hour_number == 3:
                    total_percentage = self.third_hour_percentage
                else:
                    # Use subsequent rate for hours 4-24
                    total_percentage = self.third_hour_percentage + (
                        self.subsequent_hours_percentage * Decimal(str(hour_number - 3))
                    )
            else:
                # After 24 hours, use daily rate
                days_late = int(hours_late / 24)
                total_percentage = self.daily_rate_percentage * Decimal(str(days_late))
        
        # Apply max cap if set
        if self.max_fine_percentage:
            total_percentage = min(total_percentage, self.max_fine_percentage)
        
        # Calculate fine amount
        fine_amount = (base_amount * total_percentage) / Decimal('100.00')
        
        return fine_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

