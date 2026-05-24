from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone


@pytest.fixture
def sample_order_data(website, client_user):
    return {
        "title": "Test Order",
        "description": "This is a test order",
        "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
        "pages": 5,
        "academic_level": "undergraduate",
        "paper_type": "essay",
        "website": website.id,
        "client": client_user.id,
        "price": Decimal("100.00"),
    }


@pytest.fixture
def order(client_user, website):
    from orders.models.orders import Order

    return Order.objects.create(
        client=client_user,
        website=website,
        topic="Test Order Topic",
        number_of_pages=5,
        total_price=Decimal("100.00"),
        client_deadline=timezone.now() + timedelta(days=7),
        order_instructions="Test instructions",
        status="draft",
    )


@pytest.fixture
def other_client_order(other_client, website):
    from orders.models.orders import Order

    return Order.objects.create(
        client=other_client,
        website=website,
        topic="Other Client Order",
        number_of_pages=3,
        total_price=Decimal("50.00"),
        client_deadline=timezone.now() + timedelta(days=5),
        status="draft",
    )