from __future__ import annotations

from decimal import Decimal

import pytest


@pytest.fixture
def client_wallet(client_user, website):
    from wallets.services.client_wallet_service import ClientWalletService

    return ClientWalletService.get_wallet(website=website, client=client_user)


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