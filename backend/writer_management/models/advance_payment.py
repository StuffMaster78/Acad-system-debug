from django.db import models
from django.utils.timezone import now
from decimal import Decimal
from writer_management.models import WriterProfile
from websites.models import Website
from django.conf import settings

User = settings.AUTH_USER_MODEL

class WriterAdvancePaymentRequest(models.Model):
    """
    Tracks advance payment requests from writers.
    Advances are deducted from future earnings.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
        ('repaid', 'Repaid'),
        ('cancelled', 'Cancelled'),
    ]
    
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name='advance_requests'
    )
    
    # Request details
    requested_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Amount requested by writer"
    )
    approved_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount approved by admin (may be less than requested - counteroffer)"
    )
    disbursed_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Amount actually disbursed"
    )
    
    # Calculation at time of request
    expected_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Expected earnings calculated at request time"
    )
    max_advance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('50.00'),
        help_text="Maximum advance percentage allowed (e.g., 50%)"
    )
    max_advance_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Maximum advance amount based on expected earnings"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Request details
    reason = models.TextField(
        blank=True,
        null=True,
        help_text="Writer's reason for advance request"
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    
    # Approval details
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_advances'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Admin review notes (rejection reason or counteroffer explanation)"
    )
    
    # Disbursement details
    disbursed_at = models.DateTimeField(null=True, blank=True)
    disbursed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disbursed_advances'
    )
    
    # Repayment tracking
    repaid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Amount repaid so far"
    )
    fully_repaid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['writer', 'status']),
            models.Index(fields=['status', 'requested_at']),
        ]
    
    def __str__(self):
        return f"{self.writer.user.username} - ${self.requested_amount} - {self.status}"
    
    @property
    def outstanding_amount(self):
        """Calculate outstanding advance amount"""
        return self.disbursed_amount - self.repaid_amount
    
    @property
    def is_fully_repaid(self):
        """Check if advance is fully repaid"""
        return self.repaid_amount >= self.disbursed_amount and self.disbursed_amount > 0


class AdvanceDeduction(models.Model):
    """
    Tracks deductions from writer payments to repay advances.
    """
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    advance_request = models.ForeignKey(
        WriterAdvancePaymentRequest,
        on_delete=models.CASCADE,
        related_name='deductions'
    )
    writer_payment = models.ForeignKey(
        'writer_wallet.WriterPayment',
        on_delete=models.CASCADE,
        related_name='advance_deductions',
        null=True,
        blank=True
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Order payment from which advance was deducted"
    )
    amount_deducted = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Amount deducted from payment"
    )
    deducted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-deducted_at']
    
    def __str__(self):
        return f"Advance deduction: ${self.amount_deducted} from {self.advance_request}"

