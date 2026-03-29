import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from decimal import Decimal
from wallet.models import Wallet
from django.core.exceptions import ValidationError
from discounts.models.discount import Discount 
from django.utils.timezone import now
from referrals.models import Referral, ReferralBonusConfig
from websites.models.websites import Website


def generate_reference_id():
    return uuid.uuid4().hex[:7].upper()  # Shorten to 7 characters for readability

class Invoice(models.Model):
    """
    Represents a standalone invoice for payment requests.
    Independent of specific orders/classes - can reference them optionally.

    Attributes:
        client: User receiving the invoice (can be null if using recipient_email).
        recipient_email: Email address to send invoice to (if client not in system).
        website: Website context (multi-tenant support).
        issued_by: Admin or system actor who issued it.
        title: Short label or purpose.
        purpose: Purpose of the invoice (e.g., "Order Payment", "Class Purchase").
        description: Detailed reason/description.
        order_number: Optional reference to order number (for display purposes).
        amount: Total requested.
        due_date: Payment deadline.
        is_paid: Whether it has been settled.
        payment: Linked OrderPayment, if paid.
        reference_id: Internal ID for audit.
        payment_token: Secure token for payment link.
        token_expires_at: When payment token expires.
        email_sent: Whether invoice email has been sent.
        email_sent_at: When invoice email was sent.
        email_sent_count: Number of times email was sent.
        created_at: When invoice was issued.
        paid_at: When invoice was settled.
        
    Optional References (for tracking):
        order: Optional link to Order (if invoice is for an order).
        special_order: Optional link to SpecialOrder.
        class_purchase: Optional link to ClassPurchase.
    """

    # Recipient information
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="invoices",
        help_text="Client user (if exists in system)"
    )
    recipient_email = models.EmailField(
        help_text="Email address to send invoice to (required if client is null)"
    )
    recipient_name = models.CharField(
        max_length=255, blank=True,
        help_text="Name of recipient (for email personalization)"
    )
    
    # Multi-tenant support
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE,
        related_name="invoices",
        help_text="Website context for the invoice"
    )
    
    # Issuer information
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="issued_invoices",
        help_text="Admin/superadmin who created the invoice"
    )
    
    # Invoice details
    title = models.CharField(max_length=200, help_text="Invoice title/purpose")
    purpose = models.CharField(
        max_length=100, blank=True,
        help_text="Purpose of invoice (e.g., 'Order Payment', 'Class Purchase')"
    )
    description = models.TextField(blank=True, help_text="Detailed description")
    order_number = models.CharField(
        max_length=100, blank=True,
        help_text="Optional order/reference number for display"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    
    # Payment method preference (can be changed when processing payment)
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Preferred payment method: wallet, stripe, paypal, bank_transfer, etc."
    )
    
    # Payment status
    is_paid = models.BooleanField(default=False)
    payment = models.OneToOneField(
        'OrderPayment', on_delete=models.SET_NULL,
        null=True, blank=True, related_name="invoice",
        help_text="Linked payment record when paid"
    )
    
    # Payment link
    payment_token = models.CharField(
        max_length=128, unique=True, null=True, blank=True,
        help_text="Secure token for payment link"
    )
    token_expires_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When payment token expires"
    )
    custom_payment_link = models.URLField(
        max_length=500, null=True, blank=True,
        help_text="Optional custom payment link (overrides default generated link if set)"
    )
    
    # Email tracking
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    email_sent_count = models.IntegerField(default=0)
    
    # Optional references (for tracking purposes only)
    order = models.ForeignKey(
        'orders.Order', on_delete=models.SET_NULL,
        null=True, blank=True, related_name="invoices",
        help_text="Optional reference to order"
    )
    special_order = models.ForeignKey(
        'special_orders.SpecialOrder', on_delete=models.SET_NULL,
        null=True, blank=True, related_name="invoices",
        help_text="Optional reference to special order"
    )
    class_purchase = models.ForeignKey(
        'class_management.ClassPurchase', on_delete=models.SET_NULL,
        null=True, blank=True, related_name="invoices",
        help_text="Optional reference to class purchase"
    )
    
    # Audit fields
    reference_id = models.CharField(
        max_length=64, unique=True, default=generate_reference_id,
        help_text="Unique invoice reference number"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            # Single field indexes for commonly filtered fields
            models.Index(fields=['reference_id']),
            models.Index(fields=['payment_token']),
            models.Index(fields=['is_paid']),
            models.Index(fields=['created_at']),
            models.Index(fields=['client']),
            models.Index(fields=['website']),
            models.Index(fields=['due_date']),
            # Composite indexes for common query patterns
            models.Index(fields=['is_paid', 'due_date']),  # For overdue queries
            models.Index(fields=['website', 'is_paid']),  # Multi-tenant + status filtering
            models.Index(fields=['client', 'is_paid']),  # Client invoices by status
            models.Index(fields=['website', 'created_at']),  # Multi-tenant with date ordering
            models.Index(fields=['is_paid', 'created_at']),  # Status with date ordering
        ]

    def __str__(self):
        return f"Invoice #{self.reference_id} - ${self.amount} - {self.recipient_email}"
    
    def get_recipient_email(self):
        """Get recipient email (from client or recipient_email field)."""
        if self.client:
            return self.client.email
        return self.recipient_email
    
    def get_recipient_name(self):
        """Get recipient name (from client or recipient_name field)."""
        if self.client:
            return self.client.get_full_name() or self.client.username
        return self.recipient_name or self.recipient_email.split('@')[0]
    
    def is_overdue(self):
        """Check if invoice is overdue."""
        if self.is_paid:
            return False
        return timezone.now().date() > self.due_date
    
    def is_token_valid(self):
        """Check if payment token is still valid."""
        if not self.payment_token or not self.token_expires_at:
            return False
        return timezone.now() < self.token_expires_at