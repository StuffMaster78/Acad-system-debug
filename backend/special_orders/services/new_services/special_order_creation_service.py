from __future__ import annotations

from decimal import Decimal
from functools import partial
from typing import Any

from django.db import transaction
from django.utils import timezone

from special_orders.constants import (
    FundingMilestoneType,
    SpecialOrderOrigin,
    SpecialOrderPricingMode,
    SpecialOrderPriority,
    SpecialOrderStatus,
    FundingPlanStatus,
)
from special_orders.models import (
    PredefinedSpecialOrderConfig,
    PredefinedSpecialOrderDuration,
    SpecialOrder,
    SpecialOrderFundingPlan,
    SpecialOrderFundingMilestone,
    SpecialOrderPricingSnapshot,
)
from special_orders.services.new_services import (
    special_order_fixed_pricing_service,
)
from special_orders.integrations.discount_bridge import (
    SpecialOrderDiscountBridge,
)
from communications.services.thread_bootstrap_service import (
    CommunicationThreadBootstrapService,
)


class SpecialOrderCreationService:
    """
    Creates fixed and quoted special orders.

    Fixed orders can immediately create pricing snapshots and funding plans.
    Quoted orders are created as inquiries and wait for staff quote review.
    """

    @classmethod
    @transaction.atomic
    def create_quoted_order(
        cls,
        *,
        website,
        client,
        title: str,
        inquiry_details: str = "",
        budget: Decimal | None = None,
        duration_days: int | None = None,
        currency: str = "USD",
        origin: str = SpecialOrderOrigin.CLIENT_REQUEST,
        priority: str = SpecialOrderPriority.NORMAL,
        created_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> SpecialOrder:
        """
        Create an estimated or quoted special order inquiry.
        """
        cls._validate_common_inputs(
            title=title,
            currency=currency,
            duration_days=duration_days,
        )

        if budget is not None and budget < Decimal("0.00"):
            raise ValueError("Budget cannot be negative.")

        special_order = SpecialOrder.objects.create(
            website=website,
            client=client,
            pricing_mode=SpecialOrderPricingMode.QUOTED,
            status=SpecialOrderStatus.INQUIRY,
            origin=origin,
            priority=priority,
            title=title.strip(),
            inquiry_details=inquiry_details.strip(),
            budget=budget,
            duration_days=duration_days,
            currency=currency,
        )

        bootstrap_thread = partial(
            CommunicationThreadBootstrapService.bootstrap_for_special_order,
            special_order=special_order,
            created_by=created_by,
        )
        transaction.on_commit(bootstrap_thread)

        return special_order

    @classmethod
    @transaction.atomic
    def create_fixed_order(
        cls,
        *,
        website,
        client,
        predefined_config: PredefinedSpecialOrderConfig,
        predefined_duration: PredefinedSpecialOrderDuration,
        title: str | None = None,
        inquiry_details: str = "",
        currency: str = "USD",
        origin: str = SpecialOrderOrigin.CLIENT_REQUEST,
        priority: str = SpecialOrderPriority.NORMAL,
        created_by=None,
        platform: str = "",
        writer_level: str = "",
        coupon_code: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> SpecialOrder:
        """
        Create a fixed special order and immediately lock pricing.
        """
        cls._validate_fixed_config(
            website=website,
            predefined_config=predefined_config,
            predefined_duration=predefined_duration,
        )

        order_title = title or predefined_config.name

        cls._validate_common_inputs(
            title=order_title,
            currency=currency,
            duration_days=predefined_duration.duration_days,
        )

        special_order = SpecialOrder.objects.create(
            website=website,
            client=client,
            pricing_mode=SpecialOrderPricingMode.FIXED_CONFIG,
            status=SpecialOrderStatus.AWAITING_PAYMENT,
            origin=origin,
            priority=priority,
            title=order_title.strip(),
            inquiry_details=inquiry_details.strip(),
            duration_days=predefined_duration.duration_days,
            currency=currency,
            predefined_config=predefined_config,
            predefined_duration=predefined_duration,
        )

        bootstrap_thread = partial(
            CommunicationThreadBootstrapService.bootstrap_for_special_order,
            special_order=special_order,
            created_by=created_by,
        )
        transaction.on_commit(bootstrap_thread)

        gross_quote = (
            special_order_fixed_pricing_service
            .SpecialOrderFixedPricingService
            .calculate_gross_price(
                predefined_config=predefined_config,
                predefined_duration=predefined_duration,
                currency=currency,
                platform=platform,
                writer_level=writer_level,
            )
        )

        discount_result = SpecialOrderDiscountBridge.apply_discount(
            website=website,
            client=client,
            gross_amount=gross_quote.gross_amount,
            currency=currency,
            coupon_code=coupon_code,
            metadata={
                "special_order_type": "fixed",
                "predefined_config_id": predefined_config.id,
                "predefined_duration_id": predefined_duration.id,
            },
        )

        snapshot = cls._create_fixed_pricing_snapshot(
            special_order=special_order,
            predefined_config=predefined_config,
            predefined_duration=predefined_duration,
            gross_amount=gross_quote.gross_amount,
            discount_amount=discount_result.discount_amount,
            final_amount=discount_result.final_amount,
            price_quote_data={
                "line_items": gross_quote.line_items,
                "metadata": gross_quote.metadata,
                "discount": {
                    "coupon_code": coupon_code,
                    "discount_reference": discount_result.discount_reference,
                    "metadata": discount_result.metadata,
                },
            },
            created_by=created_by,
            metadata=metadata,
        )

        cls._create_fixed_funding_plan(
            special_order=special_order,
            snapshot=snapshot,
            predefined_config=predefined_config,
            locked_by=created_by,
            metadata=metadata,
        )

        return special_order

    @classmethod
    def _create_fixed_pricing_snapshot(
        cls,
        *,
        special_order: SpecialOrder,
        predefined_config: PredefinedSpecialOrderConfig,
        predefined_duration: PredefinedSpecialOrderDuration,
        gross_amount: Decimal,
        discount_amount: Decimal,
        final_amount: Decimal,
        price_quote_data: dict[str, Any],
        created_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> SpecialOrderPricingSnapshot:
        """
        Create immutable fixed pricing snapshot.
        """
        total_amount = final_amount
        deposit_amount = total_amount

        return SpecialOrderPricingSnapshot.objects.create(
            website=special_order.website,
            special_order=special_order,
            currency=special_order.currency,
            total_amount=total_amount,
            deposit_amount=deposit_amount,
            raw_data={
                "source": "fixed_config",
                "config_id": predefined_config.id,
                "config_name": predefined_config.name,
                "duration_id": predefined_duration.id,
                "duration_days": predefined_duration.duration_days,
                "base_duration_price": str(predefined_duration.price),
                "gross_amount": str(gross_amount),
                "discount_amount": str(discount_amount),
                "final_amount": str(final_amount),
                "pricing": price_quote_data,
                "created_by_id": getattr(created_by, "id", None),
                "metadata": metadata or {},
            },
        )

    @classmethod
    def _create_fixed_funding_plan(
        cls,
        *,
        special_order: SpecialOrder,
        snapshot: SpecialOrderPricingSnapshot,
        predefined_config: PredefinedSpecialOrderConfig,
        locked_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> SpecialOrderFundingPlan:
        """
        Create funding plan for a fixed special order.
        """
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
                predefined_config.requires_full_payment
            ),
            requires_full_payment_before_delivery=True,
            locked_at=timezone.now(),
            locked_by=locked_by,
            metadata={
                "source": "fixed_config_creation",
                "metadata": metadata or {},
            },
        )

        SpecialOrderFundingMilestone.objects.create(
            website=special_order.website,
            funding_plan=funding_plan,
            special_order=special_order,
            milestone_type=FundingMilestoneType.FINAL,
            sequence=1,
            label="Full payment",
            amount_due=snapshot.total_amount,
            required_before_staffing=True,
            required_before_delivery=True,
            required_before_completion=True,
        )

        return funding_plan

    @staticmethod
    def _validate_common_inputs(
        *,
        title: str,
        currency: str,
        duration_days: int | None,
    ) -> None:
        """
        Validate shared creation fields.
        """
        if not title.strip():
            raise ValueError("Special order title is required.")

        if not currency.strip():
            raise ValueError("Currency is required.")

        if duration_days is not None and duration_days <= 0:
            raise ValueError("Duration days must be greater than zero.")

    @staticmethod
    def _validate_fixed_config(
        *,
        website,
        predefined_config: PredefinedSpecialOrderConfig,
        predefined_duration: PredefinedSpecialOrderDuration,
    ) -> None:
        """
        Validate fixed special order config and duration.
        """
        if predefined_config.website.id != website.id:
            raise ValueError("Predefined config belongs to another tenant.")

        if predefined_duration.website.id != website.id:
            raise ValueError("Predefined duration belongs to another tenant.")

        if predefined_duration.predefined_order.id != predefined_config.id:
            raise ValueError("Duration does not belong to predefined config.")

        if not predefined_config.is_active:
            raise ValueError("Predefined config is inactive.")

        if not predefined_duration.is_active:
            raise ValueError("Predefined duration is inactive.")

        if predefined_duration.price <= Decimal("0.00"):
            raise ValueError("Predefined duration price must be positive.")
