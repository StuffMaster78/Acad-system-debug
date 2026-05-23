from __future__ import annotations

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from special_orders.constants import (
    FundingPlanStatus,
    SpecialOrderPricingMode,
    SpecialOrderStatus,
)
from special_orders.models import (
    PredefinedSpecialOrderConfig,
    PredefinedSpecialOrderDuration,
    SpecialOrderFundingMilestone,
    SpecialOrderFundingPlan,
)
from special_orders.services.new_services import (
    special_order_creation_service,
)
from websites.models.websites import Website


@pytest.mark.django_db
def test_fixed_special_order_creates_pricing_and_funding_plan():
    website = Website.objects.create(
        name="Main Website",
        domain="example.com",
    )
    client = get_user_model().objects.create_user(
        username="client",
        email="client@example.com",
        password="pass",
    )
    config = PredefinedSpecialOrderConfig.objects.create(
        website=website,
        name="Shadow Health",
        slug="shadow-health",
        requires_full_payment=True,
    )
    duration = PredefinedSpecialOrderDuration.objects.create(
        website=website,
        predefined_order=config,
        duration_days=3,
        price=Decimal("250.00"),
    )

    special_order = (
        special_order_creation_service
        .SpecialOrderCreationService
        .create_fixed_order(
            website=website,
            client=client,
            predefined_config=config,
            predefined_duration=duration,
            created_by=client,
        )
    )

    funding_plan = SpecialOrderFundingPlan.objects.get(
        special_order=special_order,
    )
    milestone = SpecialOrderFundingMilestone.objects.get(
        funding_plan=funding_plan,
    )

    assert special_order.pricing_mode == SpecialOrderPricingMode.FIXED_CONFIG
    assert special_order.status == SpecialOrderStatus.AWAITING_PAYMENT
    assert funding_plan.status == FundingPlanStatus.AWAITING_DEPOSIT
    assert funding_plan.total_amount == Decimal("250.00")
    assert funding_plan.deposit_amount == Decimal("250.00")
    assert funding_plan.requires_full_payment_before_staffing is True
    assert milestone.amount_due == Decimal("250.00")
    assert milestone.required_before_staffing is True
    assert milestone.required_before_delivery is True
