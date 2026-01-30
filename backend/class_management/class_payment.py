"""
Streamlined Class Payment and Installment Tracking Models.

These models live in a separate module to keep `models.py` focused on
core class/bundle structures while still providing a unified payment
abstraction for services, serializers, and admin dashboards.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from websites.models import Website

User = settings.AUTH_USER_MODEL


class ClassPayment(models.Model):
    """
    Unified model to track class payments and writer compensation.
    Links class bundles to payments and installments in a streamlined way.
    """

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("partial", "Partially Paid"),
        ("paid", "Fully Paid"),
        ("cancelled", "Cancelled"),
    ]

    WRITER_PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending Writer Payment"),
        ("scheduled", "Scheduled"),
        ("paid", "Writer Paid"),
        ("cancelled", "Cancelled"),
    ]

    class_bundle = models.ForeignKey(
        "class_management.ClassBundle",
        on_delete=models.CASCADE,
        related_name="class_payments",
        help_text="The class bundle this payment is for",
    ) 
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="class_payments",
        help_text="Website this payment belongs to",
    )
    assigned_writer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="class_payments",
        limit_choices_to={"role": "writer"},
        help_text="Writer assigned to this class bundle",
    )

    # Client payment tracking
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total amount due from client",
    )
    deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Deposit amount required",
    )
    deposit_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Deposit amount paid",
    )
    balance_remaining = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Remaining balance after all payments",
    )
    client_payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
        help_text="Status of client payments",
    )

    # Writer compensation tracking
    writer_compensation_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total compensation amount for writer",
    )
    writer_paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Amount already paid to writer",
    )
    writer_payment_status = models.CharField(
        max_length=20,
        choices=WRITER_PAYMENT_STATUS_CHOICES,
        default="pending",
        help_text="Status of writer payment",
    )

    # Installment tracking
    uses_installments = models.BooleanField(
        default=False,
        help_text="Whether this payment uses installments",
    )
    total_installments = models.PositiveIntegerField(
        default=0,
        help_text="Total number of installments",
    )
    paid_installments = models.PositiveIntegerField(
        default=0,
        help_text="Number of installments paid",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    writer_paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When writer was fully paid",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["class_bundle", "client_payment_status"]),
            models.Index(fields=["assigned_writer", "writer_payment_status"]),
            models.Index(fields=["website", "client_payment_status"]),
            models.Index(fields=["assigned_writer", "website"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"Class Payment for Bundle #{self.class_bundle_id} - {self.client_payment_status}"

    def update_client_payment_status(self) -> None:
        """Update client payment status based on payments."""
        if self.balance_remaining <= 0 and self.deposit_paid >= self.deposit_amount:
            self.client_payment_status = "paid"
        elif self.deposit_paid > 0 or self.balance_remaining < self.total_amount:
            self.client_payment_status = "partial"
        else:
            self.client_payment_status = "pending"
        self.save(update_fields=["client_payment_status"])

    def update_writer_payment_status(self) -> None:
        """Update writer payment status based on payments."""
        if self.writer_paid_amount >= self.writer_compensation_amount:
            self.writer_payment_status = "paid"
            if not self.writer_paid_at:
                self.writer_paid_at = timezone.now()
        elif self.writer_paid_amount > 0:
            self.writer_payment_status = "scheduled"
        else:
            self.writer_payment_status = "pending"
        self.save(update_fields=["writer_payment_status", "writer_paid_at"])

    def calculate_writer_compensation(self) -> Decimal:
        """
        Calculate writer compensation based on bundle pricing.
        Can be overridden by admin-set amount.
        """
        bundle = self.class_bundle

        # Check if admin set a specific compensation
        if hasattr(bundle, "writer_compensation") and bundle.writer_compensation:
            return bundle.writer_compensation

        # Default: 60% of total or per-class rate
        if bundle.price_per_class and bundle.number_of_classes:
            return (
                Decimal(str(bundle.price_per_class))
                * bundle.number_of_classes
                * Decimal("0.6")
            )
        if bundle.total_price:
            return Decimal(str(bundle.total_price)) * Decimal("0.6")

        return Decimal("0.00")

    @property
    def is_fully_paid(self) -> bool:
        """Check if client has fully paid."""
        return self.client_payment_status == "paid"

    @property
    def is_writer_paid(self) -> bool:
        """Check if writer has been fully paid."""
        return self.writer_payment_status == "paid"

    @property
    def payment_progress(self) -> float:
        """Get payment progress percentage."""
        if self.total_amount == 0:
            return 100
        paid = self.total_amount - self.balance_remaining
        return float((paid / self.total_amount) * 100)


class ClassPaymentInstallment(models.Model):
    """
    Links ClassInstallment to ClassPayment for streamlined tracking.
    """

    class_payment = models.ForeignKey(
        ClassPayment,
        on_delete=models.CASCADE,
        related_name="payment_installments",
        help_text="The class payment this installment belongs to",
    )
    class_installment = models.OneToOneField(
        "class_management.ClassInstallment",
        on_delete=models.CASCADE,
        related_name="payment_link",
        help_text="The actual installment record",
    )
    installment_number = models.PositiveIntegerField(
        help_text="Installment sequence number",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Installment amount",
    )
    is_paid = models.BooleanField(
        default=False,
        help_text="Whether this installment is paid",
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this installment was paid",
    )
    payment_record = models.ForeignKey(
        "order_payments_management.OrderPayment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="class_payment_installments",
        help_text="The payment transaction record",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["installment_number"]
        indexes = [
            models.Index(fields=["class_payment", "is_paid"]),
            models.Index(fields=["class_payment", "installment_number"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - simple repr
        status = "Paid" if self.is_paid else "Pending"
        return f"Installment #{self.installment_number} - ${self.amount} - {status}"


class ClassWriterPayment(models.Model):
    """
    Tracks individual writer payments for classes.
    Links to WriterBonus and tracks installment-based payments.
    """

    class_payment = models.ForeignKey(
        ClassPayment,
        on_delete=models.CASCADE,
        related_name="writer_payments",
        help_text="The class payment this writer payment is for",
    )
    writer_bonus = models.ForeignKey(
        "special_orders.WriterBonus",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="class_writer_payments",
        help_text="The WriterBonus record (if created)",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Payment amount to writer",
    )
    payment_type = models.CharField(
        max_length=20,
        choices=[
            ("full", "Full Payment"),
            ("installment", "Installment-Based Payment"),
            ("partial", "Partial Payment"),
        ],
        default="full",
        help_text="Type of payment",
    )
    installment_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="If installment-based, which installment this payment is for",
    )
    is_paid = models.BooleanField(
        default=False,
        help_text="Whether writer has been paid",
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When writer was paid",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["class_payment", "is_paid"]),
            models.Index(fields=["class_payment", "payment_type"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - simple repr
        status = "Paid" if self.is_paid else "Pending"
        return f"Writer Payment ${self.amount} - {status}"


