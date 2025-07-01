from django.db import models
from django.utils.timezone import now
from django.conf import settings
from websites.models import Website 
from writer_management.models.profile import WriterProfile
from orders.models import Order



class WriterPayoutPreference(models.Model):
    """
    Stores writer payout preferences.
    """
    PAYMENT_METHOD_CHOICES = [
        ("Bank Transfer", "Bank Transfer"),
        ("PayPal", "PayPal"),
        ("Crypto", "Crypto"),
        ("Mpesa", "Mpesa"),
        ("Other", "Other"),
    ]
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_payout_preference"
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile", on_delete=models.CASCADE,
        related_name="payout_preferences"
    )
    preferred_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, 
        default="Mpesa"
    )
    payout_threshold = models.DecimalField(
        max_digits=12, decimal_places=2, default=50.00,
        help_text="Minimum payout threshold."
    )
    account_details = models.JSONField(
        default=dict, blank=True,
        help_text="Payment account details (e.g., PayPal email, bank details)."
    )
    verified = models.BooleanField(
        default=False,
        help_text="Has the payout method been verified by an admin?"
    )
    allowed_currencies = models.JSONField(
        default=list, blank=True,
        help_text="Currencies allowed for this payout method."
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.writer.user.username} - {self.preferred_method}"

    def needs_verification(self):
        """Check if payout details require admin verification."""
        return not self.verified


class WriterPayment(models.Model):
    """
    Tracks payment history for writers.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_compensation"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="payments"
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text="Total payment amount."
    )
    bonuses = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0.00, help_text="Bonuses received."
    )
    fines = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0.00, help_text="Fines deducted."
    )
    tips = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text="Tips received."
    )
    payment_date = models.DateTimeField(
        auto_now_add=True, help_text="Date of payment."
    )
    description = models.TextField(
        blank=True, null=True,
        help_text="Payment description."
    )

    def __str__(self):
        return f"Payment of ${self.amount} to {self.writer.user.username} on {self.payment_date}"


class WriterEarningsHistory(models.Model):
    """
    Tracks the writer's total earnings over different time periods.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_earning_history"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="earnings_history"
    )
    period_start = models.DateTimeField(
        help_text="Start date of the earnings period."
    )
    period_end = models.DateTimeField(
        help_text="End date of the earnings period."
    )
    total_earnings = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00,
        help_text="Total earnings for the period."
    )
    orders_completed = models.PositiveIntegerField(
        default=0, 
        help_text="Number of completed orders during this period."
    )

    def __str__(self):
        return f"Earnings for {self.writer.user.username}: {self.period_start} - {self.period_end}"


# To remove since it risks being abused
class WriterEarningsReviewRequest(models.Model):
    """
    Writers can request an admin to review earnings for a specific order.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_earnings_review"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="earnings_review_requests"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="earnings_review_requests"
    )
    reason = models.TextField(
        help_text="Reason for requesting earnings review."
    )
    requested_at = models.DateTimeField(
        auto_now_add=True
    )
    resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(
        blank=True, null=True,
        help_text="Admin resolution notes."
    )

    def __str__(self):
        return f"Earnings Review Request: {self.writer.user.username} for Order {self.order.id} (Resolved: {self.resolved})"
