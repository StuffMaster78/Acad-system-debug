from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone


# `order` is defined in the root conftest.py — no duplicate here.


@pytest.fixture
def other_client_order(other_client, website):
    from orders.models.orders import Order
    from order_configs.models import PaperType

    paper_type, _ = PaperType.objects.get_or_create(
        website=website,
        name="Essay",
    )
    return Order.objects.create(
        client=other_client,
        website=website,
        topic="Other Client Order",
        paper_type=paper_type,
        total_price=Decimal("50.00"),
        client_deadline=timezone.now() + timedelta(days=5),
        order_instructions="",
        status="draft",
    )