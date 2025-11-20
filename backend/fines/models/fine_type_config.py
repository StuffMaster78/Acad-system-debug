"""
Admin-configurable fine type definitions.
Allows admins to create and manage fine types dynamically.
"""

from django.db import models
from django.utils import timezone
from decimal import Decimal
from websites.models import Website


class FineTypeConfig(models.Model):
    """
    Admin-configurable fine type definitions.
    Replaces the need for hardcoded enum values - admins can create any fine type.
    """
    
    # System-defined vs admin-defined
    IS_SYSTEM_DEFINED_CHOICES = [
        ('system', 'System-Defined (Late Submission)'),
        ('admin', 'Admin-Defined'),
    ]
    
    is_system_defined = models.CharField(
        max_length=10,
        choices=IS_SYSTEM_DEFINED_CHOICES,
        default='admin',
        help_text="System-defined types (e.g., late submission) cannot be deleted"
    )
    
    # Fine type identifier
    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique code for this fine type (e.g., 'quality_issue', 'privacy_violation')"
    )
    
    name = models.CharField(
        max_length=100,
        help_text="Display name (e.g., 'Quality Issue', 'Privacy Violation')"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Description of when this fine applies"
    )
    
    # Fine calculation
    CALCULATION_TYPE_CHOICES = [
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage of Base Amount'),
        ('progressive_hourly', 'Progressive Hourly (Late Submission Only)'),
    ]
    
    calculation_type = models.CharField(
        max_length=20,
        choices=CALCULATION_TYPE_CHOICES,
        default='fixed',
        help_text="How to calculate the fine amount"
    )
    
    # For fixed amount
    fixed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Fixed fine amount (if calculation_type is 'fixed')"
    )
    
    # For percentage
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Fine percentage (if calculation_type is 'percentage')"
    )
    
    # Base amount for percentage calculation
    BASE_AMOUNT_CHOICES = [
        ('writer_compensation', 'Writer Compensation'),
        ('total_price', 'Order Total Price'),
    ]
    
    base_amount = models.CharField(
        max_length=20,
        choices=BASE_AMOUNT_CHOICES,
        default='writer_compensation',
        null=True,
        blank=True,
        help_text="Base amount for percentage calculation"
    )
    
    # Min/Max limits
    min_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum fine amount (enforced regardless of calculation)"
    )
    
    max_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum fine amount (cap for percentage calculations)"
    )
    
    # Website-specific (optional - None = applies to all websites)
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='fine_type_configs',
        null=True,
        blank=True,
        help_text="Website this fine type applies to (None = all websites)"
    )
    
    # Activation
    active = models.BooleanField(
        default=True,
        help_text="Whether this fine type is currently active"
    )
    
    # Metadata
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_fine_types',
        help_text="Admin who created this fine type"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Fine Type Config"
        verbose_name_plural = "Fine Type Configs"
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['website', 'active']),
            models.Index(fields=['is_system_defined']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['code', 'website'],
                name='unique_fine_type_per_website'
            ),
        ]
    
    def __str__(self):
        website_str = f" ({self.website.domain})" if self.website else " (All Websites)"
        return f"{self.name}{website_str}"
    
    def calculate_fine_amount(self, order=None, hours_late=None, base_amount=None):
        """
        Calculate fine amount based on configuration.
        
        Args:
            order: Order instance (optional, for getting base amounts)
            hours_late: Hours late (for progressive_hourly)
            base_amount: Explicit base amount (optional)
            
        Returns:
            Decimal: Fine amount
        """
        from decimal import ROUND_HALF_UP
        
        if self.calculation_type == 'fixed':
            amount = self.fixed_amount or Decimal('0.00')
        
        elif self.calculation_type == 'percentage':
            # Get base amount
            if base_amount is None:
                if order:
                    if self.base_amount == 'writer_compensation':
                        base_amount = order.writer_compensation or Decimal('0.00')
                    else:
                        base_amount = order.total_price or Decimal('0.00')
                else:
                    base_amount = Decimal('0.00')
            
            percentage = self.percentage or Decimal('0.00')
            amount = (base_amount * percentage) / Decimal('100.00')
        
        elif self.calculation_type == 'progressive_hourly':
            # Use LatenessFineRule for progressive hourly (late submission)
            from fines.models.late_fine_policy import LatenessFineRule
            if order:
                rule = LatenessFineRule.objects.filter(
                    website=order.website,
                    active=True
                ).order_by('-start_date').first()
                
                if rule:
                    if base_amount is None:
                        if rule.base_amount == 'writer_compensation':
                            base_amount = order.writer_compensation or Decimal('0.00')
                        else:
                            base_amount = order.total_price or Decimal('0.00')
                    
                    amount = rule.calculate_fine(hours_late or 0, base_amount)
                else:
                    # Fallback to default progressive calculation
                    from fines.services.late_fine_calculation_service import LateFineCalculationService
                    amount, _, _ = LateFineCalculationService.calculate_late_fine(order)
                    amount = amount or Decimal('0.00')
            else:
                amount = Decimal('0.00')
        else:
            amount = Decimal('0.00')
        
        # Apply min/max limits
        if self.min_amount:
            amount = max(amount, self.min_amount)
        if self.max_amount:
            amount = min(amount, self.max_amount)
        
        return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def clean(self):
        """Validate fine type configuration."""
        from django.core.exceptions import ValidationError
        
        # System-defined types cannot be changed to admin-defined
        if self.is_system_defined == 'system' and self.pk:
            old_instance = FineTypeConfig.objects.get(pk=self.pk)
            if old_instance.is_system_defined == 'system' and self.code != old_instance.code:
                raise ValidationError("Cannot change code of system-defined fine type.")
        
        # Validate calculation type requirements
        if self.calculation_type == 'fixed' and not self.fixed_amount:
            raise ValidationError("Fixed amount required for 'fixed' calculation type.")
        
        if self.calculation_type == 'percentage' and not self.percentage:
            raise ValidationError("Percentage required for 'percentage' calculation type.")
        
        # Progressive hourly only for late submission
        if self.calculation_type == 'progressive_hourly' and self.code != 'late_submission':
            raise ValidationError("Progressive hourly calculation only available for 'late_submission'.")
        
        # Validate min/max
        if self.min_amount and self.max_amount and self.min_amount > self.max_amount:
            raise ValidationError("Min amount cannot be greater than max amount.")

