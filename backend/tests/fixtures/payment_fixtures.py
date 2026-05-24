from __future__ import annotations

from decimal import Decimal

import pytest


@pytest.fixture
def client_wallet(client_user, website):
    from client_wallet.models import ClientWallet

    wallet, _ = ClientWallet.objects.get_or_create(
        client=client_user,
        website=website,
        defaults={
            "balance": Decimal("0.00"),
        },
    )
    return wallet


@pytest.fixture
def discount(website):
    from discounts.models import Discount

    return Discount.objects.create(
        website=website,
        code="TEST10",
        discount_type="percentage",
        value=Decimal("10.00"),
        is_active=True,
    )