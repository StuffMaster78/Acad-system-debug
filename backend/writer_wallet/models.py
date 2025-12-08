from django.db import models
from django.utils.timezone import now
from django.conf import settings
from websites.models import Website
from orders.models import Order  # Linking orders since statuses are tracked there

User = settings.AUTH_USER_MODEL 


class WriterWallet(models.Model):
    """
    Stores writer's balance and transaction history.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="writer_wallet"
    )
    is_locked = models.BooleanField(default=False)
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    total_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    total_fines = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    total_adjustments = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    currency = models.CharField(
        max_length=3,
        default="USD"
    )
    payment_date = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def get_payment_method(self):
        return self.writer_wallet.writer.writer_profile.payment_method

    def __str__(self):
        return f"{self.writer.username} - Balance: {self.balance} {self.currency}"


class WalletTransaction(models.Model):
    """
    Logs all transactions affecting the writer's wallet.
    """
    TRANSACTION_TYPES = [
        ("Earning", "Earning"),
        ("Bonus", "Bonus"),
        ("Reward", "Reward"),
        ("Adjustment", "Adjustment"),
        ("Fine", "Fine"),
        ("Refund Deduction", "Refund Deduction"),
        ("Payout", "Payout"),
        ("Order Payment", "Order Payment"),
        ("Other", "Other"),
    ]
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer_wallet = models.ForeignKey(
        WriterWallet,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )
    order = models.ForeignKey(
        Order,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )
    created_at = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        if not self.reference_code:
            self.reference_code = f"TXN-{now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.writer_wallet.writer.username} - {self.transaction_type}: {self.amount} ({self.reference_code})"


class WriterPaymentBatch(models.Model):
    """
    Stores bulk payment batches for tracking.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    reference_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="processed_payments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.reference_code:
            self.reference_code = f"PAYBATCH-{int(now().timestamp())}"  # Unique batch code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Batch {self.reference_code} - {'Completed' if self.completed else 'Pending'}"

class PaymentSchedule(models.Model):
    """
    Stores bi-weekly and monthly payment schedules.
    """
    SCHEDULE_TYPES = [
        ("Bi-Weekly", "Bi-Weekly"),
        ("Monthly", "Monthly"),
        ("Manual", "Manual"),  # For manual payment requests
    ]

    reference_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    schedule_type = models.CharField(max_length=10, choices=SCHEDULE_TYPES)
    scheduled_date = models.DateField()  # When payments should be processed
    processed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="processed_batches_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.reference_code:
            import time
            import random
            # Generate unique reference code with timestamp and random component
            # Format: PB{last8digits}{random4} = 14 characters (fits in 20 char limit)
            timestamp = int(time.time())
            timestamp_str = str(timestamp)[-8:]  # Last 8 digits of timestamp
            random_suffix = random.randint(1000, 9999)
            self.reference_code = f"PB{timestamp_str}{random_suffix}"
            # Ensure uniqueness
            while PaymentSchedule.objects.filter(reference_code=self.reference_code).exists():
                random_suffix = random.randint(1000, 9999)
                self.reference_code = f"PB{timestamp_str}{random_suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.schedule_type} Batch {self.reference_code} - {'Completed' if self.completed else 'Pending'}"


class ScheduledWriterPayment(models.Model):
    """
    Tracks individual writer payments within a payment batch.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    batch = models.ForeignKey(
        PaymentSchedule,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    writer_wallet = models.ForeignKey(
        WriterWallet,
        on_delete=models.CASCADE,
        related_name="scheduled_payments"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=[("Pending", "Pending"), ("Paid", "Paid")],
        default="Pending"
    )
    reference_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )
    payment_date = models.DateTimeField(
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.reference_code:
            self.reference_code = f"PAY-{int(now().timestamp())}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.writer_wallet.writer.username} - {self.amount} - {self.status}"


class PaymentOrderRecord(models.Model):
    """
    Tracks orders included in each writer's payment.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    payment = models.ForeignKey(
        ScheduledWriterPayment,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payment_records"
    )
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return f"Order {self.order.id} - ${self.amount_paid}"

class WriterPayment(models.Model):
    """
    Tracks individual payments made to writers.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_wallet_payments"
    )
    batch = models.ForeignKey(
        WriterPaymentBatch,
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True
    )
    writer_wallet = models.ForeignKey(
        WriterWallet,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    status = models.CharField(
        max_length=10,
        choices=[("Pending", "Pending"), ("Paid", "Paid")],
        default="Pending"
    )
    reference_code = models.CharField(max_length=20, unique=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.reference_code:
            self.reference_code = f"PAY-{int(now().timestamp())}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.writer_wallet.writer.username} - {self.amount} - {self.status}"


class AdminPaymentAdjustment(models.Model):
    """
    Allows admins to manually adjust writer payments.
    """
    ADJUSTMENT_TYPES = [
        ("Bonus", "Bonus"),
        ("Fine", "Fine"),
        ("Correction", "Correction"),
        ("Other", "Other"),
    ]

    ACTION = [
        ("Topup", "Topup"),
        ("Deduct", "Deduct"),
    ]

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer_wallet = models.ForeignKey(
        WriterWallet,
        on_delete=models.CASCADE,
        related_name="adjustments"
    )
    adjustment_type = models.CharField(
        max_length=20,
        choices=ADJUSTMENT_TYPES
    )
    action = models.CharField(
        max_length=10,
        choices=ACTION,
        default="Topup"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    adjusted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="adjusted_payments"
    )
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.writer_wallet.writer.username} - {self.adjustment_type}: {self.amount}"

class PaymentConfirmation(models.Model):
    """
    Writers confirm their payments before payout.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer_wallet = models.ForeignKey(
        WriterWallet,
        on_delete=models.CASCADE,
        related_name="confirmations"
    )
    payment = models.ForeignKey(
        WriterPayment,
        on_delete=models.CASCADE,
        related_name="confirmations"
    )
    confirmed = models.BooleanField(default=False)
    requested_review = models.BooleanField(default=False)
    auto_approved_at = models.DateTimeField(null=True, blank=True) 
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.writer_wallet.writer.username} - {'Confirmed' if self.confirmed else 'Pending'}"


class WriterPaymentRequest(models.Model):
    """
    Tracks manual payment requests from writers.
    """
    REQUEST_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processed', 'Processed'),
    ]
    
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer_wallet = models.ForeignKey(
        WriterWallet,
        on_delete=models.CASCADE,
        related_name="payment_requests"
    )
    requested_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Amount requested by writer"
    )
    available_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Writer's available balance at time of request"
    )
    status = models.CharField(
        max_length=20,
        choices=REQUEST_STATUS_CHOICES,
        default='pending'
    )
    reason = models.TextField(
        blank=True,
        null=True,
        help_text="Optional reason for the payment request"
    )
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payment_requests_made"
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_requests_reviewed"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Admin notes on approval/rejection"
    )
    created_at = models.DateTimeField(default=now)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Link to payment if processed
    scheduled_payment = models.ForeignKey(
        'ScheduledWriterPayment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_request"
    )
    
    def __str__(self):
        return f"{self.writer_wallet.writer.username} - ${self.requested_amount} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['writer_wallet', 'status']),
        ]