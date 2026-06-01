from __future__ import annotations

from decimal import Decimal
from typing import Any

from payments_processor.services.payment_intent_service import (
    PaymentIntentService,
)
from special_orders.models import (
    SpecialOrder,
    SpecialOrderFundingMilestone,
)
from special_orders.selectors import SpecialOrderFundingSelector


class SpecialOrderPaymentIntentBridge:
    """
    Create payment intents for special orders using payments_processor.
    """

    DEFAULT_PROVIDER = "stripe" # or config-driven

    @classmethod
    def create_external_payment_intent(
        cls,
        *,
        special_order: SpecialOrder,
        amount: Decimal,
        milestone: SpecialOrderFundingMilestone | None = None,
        provider: str | None = None,
        created_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a provider checkout session for a special order.
        """
        funding_plan = SpecialOrderFundingSelector.get_plan(
            website=special_order.website,
            special_order=special_order,
        )

        cls._validate_amount(
            amount=amount,
            remaining_balance=funding_plan.balance_amount,
        )

        milestone_id = None
        if milestone:
            cls._validate_milestone(
                special_order=special_order,
                milestone=milestone,
            )
            milestone_id = milestone.id

        intent_data = PaymentIntentService.create_intent(
            client=special_order.client,
            provider=provider or cls.DEFAULT_PROVIDER,
            purpose="special_order_payment",
            amount=amount,
            currency=funding_plan.currency,
            payable=special_order, # CRITICAL
            metadata={
                "payable_type": "special_order",
                "payable_id": str(special_order.id),
                "funding_plan_id": str(funding_plan.id),
                "milestone_id": str(milestone_id)
                if milestone_id
                else None,
                **(metadata or {}),
            },
            reference_prefix="so",
        )

        return intent_data

    @staticmethod
    def _validate_amount(
        *,
        amount: Decimal,
        remaining_balance: Decimal,
    ) -> None:
        if amount <= Decimal("0.00"):
            raise ValueError("Amount must be greater than zero.")

        if amount > remaining_balance:
            raise ValueError("Amount exceeds remaining balance.")

    @staticmethod
    def _validate_milestone(
        *,
        special_order: SpecialOrder,
        milestone: SpecialOrderFundingMilestone,
    ) -> None:
        if milestone.special_order_id != special_order.id:
            raise ValueError("Milestone does not belong to this order.")

        if milestone.website_id != special_order.website_id:
            raise ValueError("Cross-tenant milestone detected.")