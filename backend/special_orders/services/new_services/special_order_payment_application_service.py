from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import IntegrityError, transaction
from django.utils import timezone

from special_orders.constants import (
    FundingMilestoneStatus,
    FundingPlanStatus,
    PaymentApplicationSource,
    PaymentApplicationStatus,
    SpecialOrderStatus,
)
from special_orders.models import (
    SpecialOrder,
    SpecialOrderFundingMilestone,
    SpecialOrderFundingPlan,
    SpecialOrderPaymentApplication,
)


class SpecialOrderPaymentApplicationService:
    """
    Apply funds to a special order funding plan exactly once.

    This replaces the old InstallmentPayment.mark_paid() pattern, which
    directly marked installments as paid and linked to the legacy
    order_payments_management.OrderPayment model. The new flow keeps money
    application local, idempotent, tenant-scoped, and ledger-ready.
    """

    @classmethod
    @transaction.atomic
    def apply_payment(
        cls,
        *,
        special_order: SpecialOrder,
        amount: Decimal,
        source: str,
        idempotency_key: str,
        milestone: SpecialOrderFundingMilestone | None = None,
        payment_intent_reference: str | None = None,
        payment_transaction_reference: str | None = None,
        wallet_transaction_reference: str | None = None,
        ledger_entry_reference: str | None = None,
        applied_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> SpecialOrderPaymentApplication:
        """
        Apply a payment amount to a special order funding plan.

        Args:
            special_order:
                Special order receiving the funds.
            amount:
                Amount to apply.
            source:
                Wallet, external, split, or admin adjustment source.
            idempotency_key:
                Unique key preventing duplicate application.
            milestone:
                Optional funding milestone receiving the funds.
            payment_intent_reference:
                Optional payments_processor PaymentIntent reference.
            payment_transaction_reference:
                Optional payments_processor PaymentTransaction reference.
            wallet_transaction_reference:
                Optional wallet transaction reference.
            ledger_entry_reference:
                Optional ledger journal entry reference.
            applied_by:
                User or system actor applying the payment.
            metadata:
                Extra application metadata.

        Returns:
            Existing or newly applied SpecialOrderPaymentApplication.
        """
        cls._validate_amount(amount=amount)
        cls._validate_source(source=source)
        cls._validate_idempotency_key(idempotency_key=idempotency_key)

        funding_plan = cls._get_locked_funding_plan(
            special_order=special_order,
        )

        cls._validate_tenant(
            special_order=special_order,
            funding_plan=funding_plan,
            milestone=milestone,
        )
        cls._validate_plan_can_receive_payment(funding_plan=funding_plan)

        existing_application = (
            SpecialOrderPaymentApplication.objects.filter(
                website=special_order.website,
                idempotency_key=idempotency_key,
            )
            .select_for_update()
            .first()
        )
        if existing_application is not None:
            return existing_application

        applied_amount = cls._get_allowed_application_amount(
            funding_plan=funding_plan,
            milestone=milestone,
            amount=amount,
        )

        try:
            payment_application = (
                SpecialOrderPaymentApplication.objects.create(
                    website=special_order.website,
                    special_order=special_order,
                    funding_plan=funding_plan,
                    milestone=milestone,
                    source=source,
                    status=PaymentApplicationStatus.APPLIED,
                    amount=applied_amount,
                    currency=funding_plan.currency,
                    idempotency_key=idempotency_key,
                    payment_intent_reference=payment_intent_reference,
                    payment_transaction_reference=(
                        payment_transaction_reference
                    ),
                    wallet_transaction_reference=wallet_transaction_reference,
                    ledger_entry_reference=ledger_entry_reference,
                    applied_at=timezone.now(),
                    applied_by=applied_by,
                    metadata=metadata or {},
                )
            )
        except IntegrityError:
            return SpecialOrderPaymentApplication.objects.select_for_update().get(
                website=special_order.website,
                idempotency_key=idempotency_key,
            )

        cls._apply_to_milestone(
            milestone=milestone,
            amount=applied_amount,
        )
        cls._apply_to_funding_plan(
            funding_plan=funding_plan,
            amount=applied_amount,
        )
        cls._sync_special_order_status(
            special_order=special_order,
            funding_plan=funding_plan,
        )

        return payment_application

    @staticmethod
    def _validate_amount(*, amount: Decimal) -> None:
        """
        Validate incoming payment amount.
        """
        if amount <= Decimal("0.00"):
            raise ValueError("Payment amount must be greater than zero.")

    @staticmethod
    def _validate_source(*, source: str) -> None:
        """
        Validate payment application source.
        """
        valid_sources = {
            PaymentApplicationSource.WALLET,
            PaymentApplicationSource.EXTERNAL,
            PaymentApplicationSource.SPLIT,
            PaymentApplicationSource.ADMIN_ADJUSTMENT,
        }

        if source not in valid_sources:
            raise ValueError("Invalid payment application source.")

    @staticmethod
    def _validate_idempotency_key(*, idempotency_key: str) -> None:
        """
        Validate idempotency key.
        """
        if not idempotency_key.strip():
            raise ValueError("Idempotency key is required.")

    @staticmethod
    def _get_locked_funding_plan(
        *,
        special_order: SpecialOrder,
    ) -> SpecialOrderFundingPlan:
        """
        Lock the funding plan row to prevent double application races.
        """
        return SpecialOrderFundingPlan.objects.select_for_update().get(
            website=special_order.website,
            special_order=special_order,
        )

    @staticmethod
    def _validate_tenant(
        *,
        special_order: SpecialOrder,
        funding_plan: SpecialOrderFundingPlan,
        milestone: SpecialOrderFundingMilestone | None,
    ) -> None:
        """
        Ensure all objects belong to the same tenant and order.
        """
        if funding_plan.website_id != special_order.website_id:
            raise ValueError("Funding plan does not belong to this tenant.")

        if funding_plan.special_order_id != special_order.id:
            raise ValueError("Funding plan does not belong to this order.")

        if milestone is None:
            return

        if milestone.website_id != special_order.website_id:
            raise ValueError("Milestone does not belong to this tenant.")

        if milestone.special_order_id != special_order.id:
            raise ValueError("Milestone does not belong to this order.")

        if milestone.funding_plan_id != funding_plan.id:
            raise ValueError("Milestone does not belong to this funding plan.")

    @staticmethod
    def _validate_plan_can_receive_payment(
        *,
        funding_plan: SpecialOrderFundingPlan,
    ) -> None:
        """
        Block payments on terminal funding plans.
        """
        blocked_statuses = {
            FundingPlanStatus.CANCELLED,
            FundingPlanStatus.REFUNDED,
        }

        if funding_plan.status in blocked_statuses:
            raise ValueError("Funding plan cannot receive payments.")

    @staticmethod
    def _get_allowed_application_amount(
        *,
        funding_plan: SpecialOrderFundingPlan,
        milestone: SpecialOrderFundingMilestone | None,
        amount: Decimal,
    ) -> Decimal:
        """
        Prevent overfunding.

        The caller should normally pass the exact amount due. This method
        rejects anything above the remaining balance.
        """
        if milestone is not None:
            remaining = milestone.balance_amount
        else:
            remaining = funding_plan.balance_amount

        if amount > remaining:
            raise ValueError("Payment amount exceeds remaining balance.")

        return amount

    @staticmethod
    def _apply_to_milestone(
        *,
        milestone: SpecialOrderFundingMilestone | None,
        amount: Decimal,
    ) -> None:
        """
        Apply amount to milestone and update milestone status.
        """
        if milestone is None:
            return

        milestone.funded_amount += amount

        if milestone.funded_amount >= milestone.amount_due:
            milestone.status = FundingMilestoneStatus.PAID
        elif milestone.funded_amount > Decimal("0.00"):
            milestone.status = FundingMilestoneStatus.PARTIALLY_PAID

        milestone.save(
            update_fields=[
                "funded_amount",
                "status",
                "updated_at",
            ]
        )

    @staticmethod
    def _apply_to_funding_plan(
        *,
        funding_plan: SpecialOrderFundingPlan,
        amount: Decimal,
    ) -> None:
        """
        Apply amount to funding plan and update funding status.
        """
        funding_plan.funded_amount += amount

        if funding_plan.funded_amount >= funding_plan.total_amount:
            funding_plan.status = FundingPlanStatus.FUNDED
        elif funding_plan.funded_amount >= funding_plan.deposit_amount:
            funding_plan.status = FundingPlanStatus.PARTIALLY_FUNDED
        elif funding_plan.funded_amount > Decimal("0.00"):
            funding_plan.status = FundingPlanStatus.AWAITING_DEPOSIT

        funding_plan.save(
            update_fields=[
                "funded_amount",
                "status",
                "updated_at",
            ]
        )

    @staticmethod
    def _sync_special_order_status(
        *,
        special_order: SpecialOrder,
        funding_plan: SpecialOrderFundingPlan,
    ) -> None:
        """
        Reflect funding progress on the business-facing order status.
        """
        from special_orders.services.new_services.special_order_state_service import (
            SpecialOrderStateService,
        )

        if funding_plan.status == FundingPlanStatus.FUNDED:
            to_status = SpecialOrderStatus.READY_FOR_STAFFING
        elif funding_plan.status == FundingPlanStatus.PARTIALLY_FUNDED:
            to_status = SpecialOrderStatus.PARTIALLY_FUNDED
        else:
            to_status = SpecialOrderStatus.AWAITING_PAYMENT

        if special_order.status == to_status:
            return

        SpecialOrderStateService.transition(
            special_order=special_order,
            to_status=to_status,
            reason="Funding status synchronized after payment application.",
        )