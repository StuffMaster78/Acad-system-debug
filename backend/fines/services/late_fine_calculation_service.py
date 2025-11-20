"""
Service for calculating progressive hourly lateness fines.
"""

from django.utils import timezone
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Tuple

from django.db import models
from orders.models import Order
from fines.models import Fine, FineType, FineStatus
from fines.models.late_fine_policy import LatenessFineRule


class LateFineCalculationService:
    """
    Calculates progressive hourly lateness fines based on configured rules.
    """
    
    @staticmethod
    def calculate_late_fine(order: Order) -> Tuple[Optional[Decimal], str, Optional[LatenessFineRule]]:
        """
        Calculate late fine amount for an order.
        
        Args:
            order: The order to calculate fine for
            
        Returns:
            Tuple[Optional[Decimal], str, Optional[LatenessFineRule]]:
                - Fine amount (None if not late or no rule)
                - Reason string
                - LatenessFineRule used (if any)
        """
        # Check if order was submitted
        if not order.submitted_at:
            return None, "Order not yet submitted", None
        
        # Check if order has a deadline
        deadline = order.client_deadline or order.writer_deadline
        if not deadline:
            return None, "Order has no deadline set", None
        
        # Check if order is late
        if order.submitted_at <= deadline:
            return None, "Order submitted on time", None
        
        # Calculate hours late
        delay = order.submitted_at - deadline
        hours_late = delay.total_seconds() / 3600
        
        # Get active lateness fine rule for website
        rule = LatenessFineRule.objects.filter(
            website=order.website,
            active=True
        ).filter(
            models.Q(end_date__gte=timezone.now()) | models.Q(end_date__isnull=True),
            start_date__lte=timezone.now()
        ).order_by('-start_date').first()
        
        # If no rule found, use default progressive calculation
        if not rule:
            fine_amount = LateFineCalculationService._default_progressive_calculation(
                hours_late, order
            )
            reason = f"Auto-issued lateness fine: {round(hours_late, 2)}h late (default calculation)"
            return fine_amount, reason, None
        
        # Use rule-based calculation
        base_amount = LateFineCalculationService._get_base_amount(order, rule.base_amount)
        fine_amount = rule.calculate_fine(hours_late, base_amount)
        
        reason = (
            f"Auto-issued lateness fine: {round(hours_late, 2)}h late. "
            f"Calculation: {rule.calculation_mode}, Base: {rule.base_amount}"
        )
        
        return fine_amount, reason, rule
    
    @staticmethod
    def _get_base_amount(order: Order, base_type: str) -> Decimal:
        """Get base amount for fine calculation."""
        if base_type == 'writer_compensation':
            return order.writer_compensation or Decimal('0.00')
        else:  # total_price
            return order.total_price or Decimal('0.00')
    
    @staticmethod
    def _default_progressive_calculation(hours_late: float, order: Order) -> Decimal:
        """
        Default progressive calculation: 5% first hour, 10% second hour, etc.
        Cumulative mode by default.
        """
        base_amount = order.writer_compensation or order.total_price or Decimal('0.00')
        
        if base_amount <= 0:
            return Decimal('0.00')
        
        # Progressive cumulative: 5% + 10% + 15% + ...
        total_percentage = Decimal('0.00')
        
        # First hour: 5%
        if hours_late >= 1:
            total_percentage += Decimal('5.00')
        
        # Second hour: 10% (cumulative = 5% + 10% = 15%)
        if hours_late >= 2:
            total_percentage += Decimal('10.00')
        
        # Third hour: 15% (cumulative = 15% + 15% = 30%)
        if hours_late >= 3:
            total_percentage += Decimal('15.00')
        
        # Hours 4-24: 5% per hour
        if hours_late > 3:
            additional_hours = min(int(hours_late - 3), 21)  # Up to hour 24
            total_percentage += Decimal('5.00') * Decimal(str(additional_hours))
        
        # After 24 hours: 20% per day
        if hours_late >= 24:
            days_late = int((hours_late - 24) / 24) + 1
            total_percentage += Decimal('20.00') * Decimal(str(days_late))
        
        # Cap at 100% (can't fine more than base amount)
        total_percentage = min(total_percentage, Decimal('100.00'))
        
        fine_amount = (base_amount * total_percentage) / Decimal('100.00')
        return fine_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

