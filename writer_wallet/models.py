from django.db import models
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from orders.models import Order  # Linking orders since statuses are tracked there

User = get_user_model()


class WriterWallet(models.Model):
    """
    Stores writer's balance and transaction history.
    """
    writer = models.OneToOneField(User, on_delete=models.CASCADE, related_name="writer_wallet")
    is_locked = models.BooleanField(default=False)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_fines = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_adjustments = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default="USD")  # Default to USD
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

    writer_wallet = models.ForeignKey(WriterWallet, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference_code = models.CharField(max_length=20, unique=True, blank=True)  # System-generated
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
    reference_code = models.CharField(max_length=20, unique=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="processed_payments")
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
    ]

    reference_code = models.CharField(max_length=20, unique=True, blank=True)
    schedule_type = models.CharField(max_length=10, choices=SCHEDULE_TYPES)
    scheduled_date = models.DateField()  # When payments should be processed
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="processed_batches")
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.reference_code:
            self.reference_code = f"PAYBATCH-{int(now().timestamp())}"  # Unique batch code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.schedule_type} Batch {self.reference_code} - {'Completed' if self.completed else 'Pending'}"


class ScheduledWriterPayment(models.Model):
    """
    Tracks individual writer payments within a payment batch.
    """
    batch = models.ForeignKey(PaymentSchedule, on_delete=models.CASCADE, related_name="payments")
    writer_wallet = models.ForeignKey(WriterWallet, on_delete=models.CASCADE, related_name="scheduled_payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=[("Pending", "Pending"), ("Paid", "Paid")], default="Pending")
    reference_code = models.CharField(max_length=20, unique=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)

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
    payment = models.ForeignKey(ScheduledWriterPayment, on_delete=models.CASCADE, related_name="orders")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payment_records")
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Order {self.order.id} - ${self.amount_paid}"

class WriterPayment(models.Model):
    """
    Tracks individual payments made to writers.
    """
    batch = models.ForeignKey(WriterPaymentBatch, on_delete=models.CASCADE, related_name="payments", null=True, blank=True)
    writer_wallet = models.ForeignKey(WriterWallet, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=[("Pending", "Pending"), ("Paid", "Paid")], default="Pending")
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

    writer_wallet = models.ForeignKey(WriterWallet, on_delete=models.CASCADE, related_name="adjustments")
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    adjusted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="adjusted_payments")
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.writer_wallet.writer.username} - {self.adjustment_type}: {self.amount}"

class PaymentConfirmation(models.Model):
    """
    Writers confirm their payments before payout.
    """
    writer_wallet = models.ForeignKey(WriterWallet, on_delete=models.CASCADE, related_name="confirmations")
    payment = models.ForeignKey(WriterPayment, on_delete=models.CASCADE, related_name="confirmations")
    confirmed = models.BooleanField(default=False)
    requested_review = models.BooleanField(default=False)
    auto_approved_at = models.DateTimeField(null=True, blank=True) 
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.writer_wallet.writer.username} - {'Confirmed' if self.confirmed else 'Pending'}"