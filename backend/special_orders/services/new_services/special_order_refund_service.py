from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from special_orders.constants import (
    FundingMilestoneStatus,
    FundingPlanStatus,
    PaymentApplicationStatus,
    RefundApplicationStatus,
    RefundDestination,
    SpecialOrderStatus,
)
from special_orders.models import (
    SpecialOrderPaymentApplication,
    SpecialOrderRefundApplication,
)
from special_orders.services.new_services.special_order_state_service import (
    SpecialOrderStateService,
)


class SpecialOrderRefundService:
    """
    Records and applies refunds against special order payment applications.

    This service does not call payment providers directly. External or wallet
    refund execution should happen before calling `apply_refund`.
    """

    @classmethod
    @transaction.atomic
    def apply_refund(
        cls,
        *,
        payment_application: SpecialOrderPaymentApplication,
        amount: Decimal,
        destination: str = RefundDestination.ORIGINAL_PAYMENT_METHOD,
        refund_transaction_reference: str | None = None,
        reversal_ledger_entry_reference: str | None = None,
        requested_by=None,
        approved_by=None,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> SpecialOrderRefundApplication:
        """
        Apply a refund against a previously applied payment.
        """
        cls._validate_amount(amount=amount)
        cls._validate_destination(destination=destination)

        payment_application = (
            SpecialOrderPaymentApplication.objects.select_for_update()
            .select_related(
                "special_order",
                "funding_plan",
                "milestone",
            )
            .get(id=payment_application.id)
        )

        cls._validate_payment_application(
            payment_application=payment_application,
        )
        cls._validate_refundable_amount(
            payment_application=payment_application,
            amount=amount,
        )

        refund_application = SpecialOrderRefundApplication.objects.create(
            website=payment_application.website,
            special_order=payment_application.special_order,
            funding_plan=payment_application.funding_plan,
            milestone=payment_application.milestone,
            original_payment_application=payment_application,
            status=RefundApplicationStatus.REFUNDED,
            destination=destination,
            amount=amount,
            currency=payment_application.currency,
            refund_transaction_reference=refund_transaction_reference,
            reversal_ledger_entry_reference=reversal_ledger_entry_reference,
            reason=reason,
            requested_by=requested_by,
            approved_by=approved_by,
            refunded_at=timezone.now(),
            metadata=metadata or {},
        )

        cls._apply_to_milestone(
            refund_application=refund_application,
        )
        cls._apply_to_funding_plan(
            refund_application=refund_application,
        )
        cls._sync_payment_application_status(
            payment_application=payment_application,
        )
        cls._sync_special_order_status(
            refund_application=refund_application,
        )

        return refund_application

    @staticmethod
    def _validate_amount(*, amount: Decimal) -> None:
        """
        Validate refund amount.
        """
        if amount <= Decimal("0.00"):
            raise ValueError("Refund amount must be greater than zero.")

    @staticmethod
    def _validate_destination(*, destination: str) -> None:
        """
        Validate refund destination.
        """
        valid_destinations = {
            RefundDestination.WALLET,
            RefundDestination.ORIGINAL_PAYMENT_METHOD,
            RefundDestination.MANUAL,
        }

        if destination not in valid_destinations:
            raise ValueError("Invalid refund destination.")

    @staticmethod
    def _validate_payment_application(
        *,
        payment_application: SpecialOrderPaymentApplication,
    ) -> None:
        """
        Ensure payment application can be refunded.
        """
        if payment_application.status not in {
            PaymentApplicationStatus.APPLIED,
            PaymentApplicationStatus.REVERSED,
        }:
            raise ValueError("Payment application is not refundable.")

    @staticmethod
    def _validate_refundable_amount(
        *,
        payment_application: SpecialOrderPaymentApplication,
        amount: Decimal,
    ) -> None:
        """
        Prevent refunding more than applied amount.
        """
        existing_refunded_amount = sum(
            refund.amount
            for refund in SpecialOrderRefundApplication.objects.filter(
                original_payment_application=payment_application,
                status=RefundApplicationStatus.REFUNDED,
            )
        )

        refundable_amount = (
            payment_application.amount - existing_refunded_amount
        )

        if amount > refundable_amount:
            raise ValueError("Refund exceeds refundable amount.")

    @staticmethod
    def _apply_to_milestone(
        *,
        refund_application: SpecialOrderRefundApplication,
    ) -> None:
        """
        Apply refund totals to the related milestone.
        """
        milestone = refund_application.milestone

        if milestone is None:
            return

        milestone.refunded_amount += refund_application.amount

        net_funded_amount = milestone.net_funded_amount

        if net_funded_amount <= Decimal("0.00"):
            milestone.status = FundingMilestoneStatus.PENDING
        elif net_funded_amount < milestone.amount_due:
            milestone.status = FundingMilestoneStatus.PARTIALLY_PAID
        else:
            milestone.status = FundingMilestoneStatus.PAID

        milestone.save(
            update_fields=[
                "refunded_amount",
                "status",
                "updated_at",
            ]
        )

    @staticmethod
    def _apply_to_funding_plan(
        *,
        refund_application: SpecialOrderRefundApplication,
    ) -> None:
        """
        Apply refund totals to the funding plan.
        """
        funding_plan = refund_application.funding_plan

        funding_plan.refunded_amount += refund_application.amount

        net_funded_amount = funding_plan.net_funded_amount

        if net_funded_amount <= Decimal("0.00"):
            funding_plan.status = FundingPlanStatus.REFUNDED
        elif net_funded_amount < funding_plan.total_amount:
            funding_plan.status = FundingPlanStatus.PARTIALLY_REFUNDED
        else:
            funding_plan.status = FundingPlanStatus.FUNDED

        funding_plan.save(
            update_fields=[
                "refunded_amount",
                "status",
                "updated_at",
            ]
        )

    @staticmethod
    def _sync_payment_application_status(
        *,
        payment_application: SpecialOrderPaymentApplication,
    ) -> None:
        """
        Mark payment application as reversed only when fully refunded.
        """
        refunded_amount = sum(
            refund.amount
            for refund in SpecialOrderRefundApplication.objects.filter(
                original_payment_application=payment_application,
                status=RefundApplicationStatus.REFUNDED,
            )
        )

        if refunded_amount >= payment_application.amount:
            payment_application.status = PaymentApplicationStatus.REVERSED
            payment_application.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

    @staticmethod
    def _sync_special_order_status(
        *,
        refund_application: SpecialOrderRefundApplication,
    ) -> None:
        """
        Sync order status after refund.
        """
        funding_plan = refund_application.funding_plan
        special_order = refund_application.special_order

        if funding_plan.status == FundingPlanStatus.REFUNDED:
            to_status = SpecialOrderStatus.REFUNDED
        elif funding_plan.status == FundingPlanStatus.PARTIALLY_REFUNDED:
            to_status = SpecialOrderStatus.PARTIALLY_FUNDED
        else:
            return

        if special_order.status == to_status:
            return

        SpecialOrderStateService.transition(
            special_order=special_order,
            to_status=to_status,
            reason="Funding status synchronized after refund application.",
        )