from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from core.models.timestamped_model import TimeStampedModel
from special_orders.constants import (
    FundingMilestoneStatus,
    FundingMilestoneType,
    FundingPlanStatus,
    PaymentApplicationSource,
    PaymentApplicationStatus,
    RefundApplicationStatus,
    RefundDestination,
)


class SpecialOrderFundingPlan(TimeStampedModel):
    """
    Canonical funding state for a special order.

    This model is financial state only. It does not replace ledger truth.
    It mirrors the applied funding state for product workflow decisions.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_funding_plans",
    )
    special_order = models.OneToOneField(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="funding_plan",
    )

    currency = models.CharField(max_length=10, default="USD")

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    deposit_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    funded_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    refunded_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    status = models.CharField(
        max_length=50,
        choices=FundingPlanStatus.CHOICES,
        default=FundingPlanStatus.DRAFT,
    )

    requires_full_payment_before_staffing = models.BooleanField(
        default=False,
    )
    requires_full_payment_before_delivery = models.BooleanField(
        default=True,
    )

    locked_at = models.DateTimeField(null=True, blank=True)
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="locked_special_order_funding_plans",
    )

    metadata = models.JSONField(default=dict, blank=True)

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "special_order"]),
            models.Index(fields=["website", "created_at"]),
        ]

    @property
    def balance_amount(self) -> Decimal:
        """
        Return the remaining unpaid amount.
        """
        balance = self.total_amount - self.funded_amount
        return max(balance, Decimal("0.00"))

    @property
    def net_funded_amount(self) -> Decimal:
        """
        Return funded amount after refunds.
        """
        net_amount = self.funded_amount - self.refunded_amount
        return max(net_amount, Decimal("0.00"))

    def __str__(self) -> str:
        return f"FundingPlan(order={self.special_order_id})"

    if TYPE_CHECKING:
        id: int
        website_id: int
        special_order_id: int


class SpecialOrderFundingMilestone(TimeStampedModel):
    """
    Payment checkpoint for a special order.

    Replaces the old InstallmentPayment model.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_funding_milestones",
    )
    funding_plan = models.ForeignKey(
        "special_orders.SpecialOrderFundingPlan",
        on_delete=models.CASCADE,
        related_name="milestones",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="funding_milestones",
    )

    milestone_type = models.CharField(
        max_length=50,
        choices=FundingMilestoneType.CHOICES,
        default=FundingMilestoneType.PROGRESS,
    )
    status = models.CharField(
        max_length=50,
        choices=FundingMilestoneStatus.CHOICES,
        default=FundingMilestoneStatus.PENDING,
    )

    sequence = models.PositiveIntegerField()
    label = models.CharField(max_length=255)

    amount_due = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    funded_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    refunded_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    due_at = models.DateTimeField(null=True, blank=True)

    required_before_staffing = models.BooleanField(default=False)
    required_before_draft = models.BooleanField(default=False)
    required_before_delivery = models.BooleanField(default=False)
    required_before_completion = models.BooleanField(default=False)

    metadata = models.JSONField(default=dict, blank=True)

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("sequence",)
        constraints = [
            models.UniqueConstraint(
                fields=["funding_plan", "sequence"],
                name="unique_special_order_funding_milestone_sequence",
            ),
        ]
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "special_order"]),
            models.Index(fields=["funding_plan", "sequence"]),
            models.Index(fields=["website", "due_at"]),
        ]

    @property
    def balance_amount(self) -> Decimal:
        """
        Return the unpaid amount for this milestone.
        """
        balance = self.amount_due - self.funded_amount
        return max(balance, Decimal("0.00"))

    @property
    def net_funded_amount(self) -> Decimal:
        """
        Return funded amount after refunds.
        """
        net_amount = self.funded_amount - self.refunded_amount
        return max(net_amount, Decimal("0.00"))

    def __str__(self) -> str:
        return (
            f"FundingMilestone("
            f"order={self.special_order_id}, "
            f"sequence={self.sequence})"
        )

    if TYPE_CHECKING:
        id: int
        website_id: int
        funding_plan_id: int
        special_order_id: int


class SpecialOrderPaymentApplication(TimeStampedModel):
    """
    Idempotent record of funds applied to a special order.

    This is not the payment processor transaction itself. It is the local
    application of money to the special order funding plan.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_payment_applications",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="payment_applications",
    )
    funding_plan = models.ForeignKey(
        "special_orders.SpecialOrderFundingPlan",
        on_delete=models.CASCADE,
        related_name="payment_applications",
    )
    milestone = models.ForeignKey(
        "special_orders.SpecialOrderFundingMilestone",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="payment_applications",
    )

    source = models.CharField(
        max_length=50,
        choices=PaymentApplicationSource.CHOICES,
    )
    status = models.CharField(
        max_length=50,
        choices=PaymentApplicationStatus.CHOICES,
        default=PaymentApplicationStatus.PENDING,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    currency = models.CharField(max_length=10, default="USD")

    idempotency_key = models.CharField(max_length=255)

    payment_intent_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Reference to payments_processor PaymentIntent.",
    )
    payment_transaction_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Reference to payments_processor PaymentTransaction.",
    )
    wallet_transaction_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Reference to wallet transaction or wallet ledger event.",
    )
    ledger_entry_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Reference to the journal entry posted by ledger.",
    )

    applied_at = models.DateTimeField(null=True, blank=True)
    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="applied_special_order_payments",
    )

    metadata = models.JSONField(default=dict, blank=True)

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["website", "idempotency_key"],
                name="unique_special_order_payment_idempotency_per_site",
            ),
        ]
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "source"]),
            models.Index(fields=["website", "special_order"]),
            models.Index(fields=["website", "idempotency_key"]),
            models.Index(fields=["payment_intent_reference"]),
            models.Index(fields=["payment_transaction_reference"]),
        ]

    def __str__(self) -> str:
        return (
            f"PaymentApplication("
            f"order={self.special_order_id}, "
            f"amount={self.amount})"
        )

    if TYPE_CHECKING:
        id: int
        website_id: int
        special_order_id: int
        funding_plan_id: int
        milestone_id: int | None


class SpecialOrderRefundApplication(TimeStampedModel):
    """
    Tracks refunds against previously applied special order payments.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_refund_applications",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="refund_applications",
    )
    funding_plan = models.ForeignKey(
        "special_orders.SpecialOrderFundingPlan",
        on_delete=models.CASCADE,
        related_name="refund_applications",
    )
    milestone = models.ForeignKey(
        "special_orders.SpecialOrderFundingMilestone",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="refund_applications",
    )
    original_payment_application = models.ForeignKey(
        "special_orders.SpecialOrderPaymentApplication",
        on_delete=models.PROTECT,
        related_name="refund_applications",
    )

    status = models.CharField(
        max_length=50,
        choices=RefundApplicationStatus.CHOICES,
        default=RefundApplicationStatus.PENDING,
    )
    destination = models.CharField(
        max_length=50,
        choices=RefundDestination.CHOICES,
        default=RefundDestination.ORIGINAL_PAYMENT_METHOD,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    currency = models.CharField(max_length=10, default="USD")

    refund_transaction_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Reference to external or wallet refund transaction.",
    )
    reversal_ledger_entry_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Reference to the ledger reversal journal entry.",
    )

    reason = models.TextField(blank=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="requested_special_order_refunds",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_special_order_refunds",
    )
    refunded_at = models.DateTimeField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "special_order"]),
            models.Index(fields=["website", "created_at"]),
            models.Index(fields=["refund_transaction_reference"]),
        ]

    def __str__(self) -> str:
        return (
            f"RefundApplication("
            f"order={self.special_order_id}, "
            f"amount={self.amount})"
        )

    if TYPE_CHECKING:
        id: int
        website_id: int
        special_order_id: int
        funding_plan_id: int
        milestone_id: int | None
        original_payment_application_id: int