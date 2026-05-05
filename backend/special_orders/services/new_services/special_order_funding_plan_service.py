from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from django.db import transaction
from django.utils import timezone

from special_orders.constants import (
    FundingMilestoneType,
    FundingPlanStatus,
)
from special_orders.models.configs import (
    SpecialOrderMilestoneTemplateItem,
    EstimatedSpecialOrderSettings,
)
from special_orders.models.special_order import (
    SpecialOrder,
)
from special_orders.models.funding import (
    SpecialOrderFundingPlan,
    SpecialOrderFundingMilestone,
)
from special_orders.models.pricing_snapshot import (
    SpecialOrderPricingSnapshot,
)
from special_orders.models.configs import (
    SpecialOrderMilestoneTemplate,
)


class SpecialOrderFundingPlanService:
    """
    Create locked funding plans and milestones for special orders.

    Funding plans are created from accepted pricing snapshots, not from
    mutable quotes or configs.
    """

    @classmethod
    @transaction.atomic
    def create_from_pricing_snapshot(
        cls,
        *,
        special_order: SpecialOrder,
        snapshot: SpecialOrderPricingSnapshot,
        template: SpecialOrderMilestoneTemplate | None = None,
        locked_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> SpecialOrderFundingPlan:
        """
        Create a funding plan and milestones from an immutable snapshot.
        """
        cls._validate_snapshot(
            special_order=special_order,
            snapshot=snapshot,
        )

        existing_plan = SpecialOrderFundingPlan.objects.filter(
            website=special_order.website,
            special_order=special_order,
        ).first()
        if existing_plan is not None:
            return existing_plan

        settings = cls._get_settings(special_order=special_order)

        funding_plan = SpecialOrderFundingPlan.objects.create(
            website=special_order.website,
            special_order=special_order,
            currency=snapshot.currency,
            total_amount=snapshot.total_amount,
            deposit_amount=snapshot.deposit_amount,
            funded_amount=Decimal("0.00"),
            refunded_amount=Decimal("0.00"),
            status=FundingPlanStatus.AWAITING_DEPOSIT,
            requires_full_payment_before_staffing=(
                snapshot.deposit_amount >= snapshot.total_amount
            ),
            requires_full_payment_before_delivery=(
                settings.require_full_payment_before_delivery
            ),
            locked_at=timezone.now(),
            locked_by=locked_by,
            metadata=metadata or {},
        )

        if template is not None:
            cls._create_template_milestones(
                funding_plan=funding_plan,
                special_order=special_order,
                template=template,
            )
        else:
            cls._create_default_milestones(
                funding_plan=funding_plan,
                special_order=special_order,
                settings=settings,
            )

        return funding_plan

    @classmethod
    def _create_default_milestones(
        cls,
        *,
        funding_plan: SpecialOrderFundingPlan,
        special_order: SpecialOrder,
        settings: EstimatedSpecialOrderSettings,
    ) -> None:
        """
        Create deposit and final milestones from funding settings.
        """
        total_amount = funding_plan.total_amount
        deposit_amount = funding_plan.deposit_amount
        balance_amount = total_amount - deposit_amount

        if deposit_amount > Decimal("0.00"):
            SpecialOrderFundingMilestone.objects.create(
                website=special_order.website,
                funding_plan=funding_plan,
                special_order=special_order,
                milestone_type=FundingMilestoneType.DEPOSIT,
                sequence=1,
                label="Deposit",
                amount_due=deposit_amount,
                required_before_staffing=(
                    settings.require_deposit_before_staffing
                ),
                required_before_delivery=False,
            )

        if balance_amount > Decimal("0.00"):
            SpecialOrderFundingMilestone.objects.create(
                website=special_order.website,
                funding_plan=funding_plan,
                special_order=special_order,
                milestone_type=FundingMilestoneType.FINAL,
                sequence=2,
                label="Final balance",
                amount_due=balance_amount,
                required_before_staffing=False,
                required_before_delivery=(
                    settings.require_full_payment_before_delivery
                ),
            )

    @classmethod
    def _create_template_milestones(
        cls,
        *,
        funding_plan: SpecialOrderFundingPlan,
        special_order: SpecialOrder,
        template: SpecialOrderMilestoneTemplate,
    ) -> None:
        """
        Create milestones from a reusable milestone template.
        """
        template_items = (
            SpecialOrderMilestoneTemplateItem.objects.filter(
                template=template,
            )
            .order_by("sequence")
        )

        for item in template_items:
            amount_due = cls._calculate_percentage_amount(
                total_amount=funding_plan.total_amount,
                percentage=item.percentage,
            )

            SpecialOrderFundingMilestone.objects.create(
                website=special_order.website,
                funding_plan=funding_plan,
                special_order=special_order,
                milestone_type=FundingMilestoneType.PROGRESS,
                sequence=item.sequence,
                label=item.label,
                amount_due=amount_due,
                required_before_staffing=item.required_before_staffing,
                required_before_delivery=item.required_before_delivery,
            )

    @staticmethod
    def _calculate_percentage_amount(
        *,
        total_amount: Decimal,
        percentage: Decimal,
    ) -> Decimal:
        """
        Calculate a milestone amount from a percentage.
        """
        amount = total_amount * (percentage / Decimal("100.00"))
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _validate_snapshot(
        *,
        special_order: SpecialOrder,
        snapshot: SpecialOrderPricingSnapshot,
    ) -> None:
        """
        Validate snapshot belongs to the special order and tenant.
        """
        if snapshot.website_id != special_order.website_id:
            raise ValueError("Pricing snapshot belongs to another tenant.")

        if snapshot.special_order_id != special_order.id:
            raise ValueError("Pricing snapshot belongs to another order.")

        if snapshot.total_amount <= Decimal("0.00"):
            raise ValueError("Snapshot total amount must be greater than zero.")

        if snapshot.deposit_amount < Decimal("0.00"):
            raise ValueError("Snapshot deposit amount cannot be negative.")

        if snapshot.deposit_amount > snapshot.total_amount:
            raise ValueError("Snapshot deposit exceeds total amount.")

    @staticmethod
    def _get_settings(
        *,
        special_order: SpecialOrder,
    ) -> EstimatedSpecialOrderSettings:
        """
        Return tenant settings or create sane defaults.
        """
        settings, _created = EstimatedSpecialOrderSettings.objects.get_or_create(
            website=special_order.website,
        )
        return settings