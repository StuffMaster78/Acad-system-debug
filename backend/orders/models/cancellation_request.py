"""
Cancellation Request Model
Handles client requests for order cancellation with deadline-based forfeiture.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = settings.AUTH_USER_MODEL


class CancellationRequest(models.Model):
    """
    Tracks client requests for order cancellation.
    Includes deadline-based forfeiture calculation.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),  # Request was cancelled by client
    ]
    
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='cancellation_requests'
    )
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cancellation_requests',
        help_text="Client who requested the cancellation"
    )
    reason = models.TextField(
        help_text="Client's reason for requesting cancellation"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Status of the cancellation request"
    )
    
    # Deadline-based forfeiture calculation
    deadline_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Percentage of deadline elapsed when cancellation was requested"
    )
    forfeiture_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Percentage of order amount to forfeit (calculated based on deadline percentage)"
    )
    forfeiture_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Actual amount to forfeit (calculated from forfeiture_percentage)"
    )
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Amount to refund to client (total_price - forfeiture_amount)"
    )
    
    # Admin review
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_cancellation_requests',
        help_text="Admin who reviewed this request"
    )
    review_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Admin notes on the cancellation request"
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the request was reviewed"
    )
    
    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['order', 'status']),
            models.Index(fields=['requested_by', 'status']),
            models.Index(fields=['status', 'requested_at']),
        ]
        verbose_name = "Cancellation Request"
        verbose_name_plural = "Cancellation Requests"
    
    def __str__(self):
        return f"Cancellation Request #{self.id} - Order #{self.order.id} ({self.status})"
    
    def calculate_forfeiture(self, threshold_percentage=Decimal('50.00')):
        """
        Calculate forfeiture based on deadline percentage.
        
        Args:
            threshold_percentage: Percentage threshold (default 50%)
                - Below threshold: No forfeiture (full refund)
                - Above threshold: Progressive forfeiture based on deadline percentage
        
        Returns:
            Tuple[Decimal, Decimal, Decimal]: (forfeiture_percentage, forfeiture_amount, refund_amount)
        """
        from order_payments_management.services.payment_reminder_service import PaymentReminderService
        
        # Calculate deadline percentage
        deadline_pct = PaymentReminderService.get_deadline_percentage(self.order)
        self.deadline_percentage = deadline_pct
        
        # Get order total price
        total_price = self.order.total_price or Decimal('0.00')
        
        # If deadline percentage is below threshold, no forfeiture
        if deadline_pct < threshold_percentage:
            self.forfeiture_percentage = Decimal('0.00')
            self.forfeiture_amount = Decimal('0.00')
            self.refund_amount = total_price
        else:
            # Progressive forfeiture: the more deadline elapsed, the more forfeited
            # Formula: forfeiture = (deadline_pct - threshold) / (100 - threshold) * max_forfeiture_pct
            # Max forfeiture is 80% (to always refund at least 20%)
            max_forfeiture_pct = Decimal('80.00')
            excess_pct = deadline_pct - threshold_percentage
            available_range = Decimal('100.00') - threshold_percentage
            
            if available_range > 0:
                forfeiture_pct = (excess_pct / available_range) * max_forfeiture_pct
                self.forfeiture_percentage = min(forfeiture_pct, max_forfeiture_pct)
            else:
                self.forfeiture_percentage = max_forfeiture_pct
            
            # Calculate amounts
            self.forfeiture_amount = (total_price * self.forfeiture_percentage) / Decimal('100.00')
            self.refund_amount = total_price - self.forfeiture_amount
        
        self.save(update_fields=[
            'deadline_percentage', 'forfeiture_percentage', 
            'forfeiture_amount', 'refund_amount'
        ])
        
        return self.forfeiture_percentage, self.forfeiture_amount, self.refund_amount
    
    def approve(self, reviewed_by, review_notes=None):
        """Approve the cancellation request and cancel the order."""
        from orders.services.transition_helper import OrderTransitionHelper
        
        if self.status != 'pending':
            raise ValueError(f"Cannot approve request in status '{self.status}'")
        
        self.status = 'approved'
        self.reviewed_by = reviewed_by
        self.review_notes = review_notes
        self.reviewed_at = timezone.now()
        self.save()
        
        # Cancel the order
        OrderTransitionHelper.transition_order(
            order=self.order,
            target_status='cancelled',
            user=reviewed_by,
            reason=f"Cancellation approved. {self.reason}",
            action="cancel_order",
            is_automatic=False,
            metadata={
                "cancellation_request_id": self.id,
                "forfeiture_amount": str(self.forfeiture_amount),
                "refund_amount": str(self.refund_amount),
                "deadline_percentage": str(self.deadline_percentage),
            }
        )
        
        return self
    
    def reject(self, reviewed_by, review_notes):
        """Reject the cancellation request."""
        if self.status != 'pending':
            raise ValueError(f"Cannot reject request in status '{self.status}'")
        
        self.status = 'rejected'
        self.reviewed_by = reviewed_by
        self.review_notes = review_notes
        self.reviewed_at = timezone.now()
        self.save()
        
        return self

