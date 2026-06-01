from __future__ import annotations

from decimal import Decimal

import pytest


def _ensure_ledger_accounts(website):
    """Create the minimum ledger accounts required for wallet payment tests."""
    from ledger.models.ledger_account import LedgerAccount
    from ledger.constants import LedgerAccountStatus

    ACCOUNTS = [
        ("CLIENT_WALLET_LIABILITY", "Client Wallet Liability", "LIABILITY"),
        ("WRITER_WALLET_LIABILITY", "Writer Wallet Liability", "LIABILITY"),
        ("ORDER_FUNDS_HELD", "Order Funds Held", "LIABILITY"),
        ("GATEWAY_CLEARING", "Gateway Clearing", "ASSET"),
        ("REFUND_CLEARING", "Refund Clearing", "ASSET"),
        ("PLATFORM_ADJUSTMENTS", "Platform Adjustments", "EXPENSE"),
    ]
    for code, name, account_type in ACCOUNTS:
        LedgerAccount.objects.get_or_create(
            website=website,
            code=code,
            defaults={
                "name": name,
                "account_type": account_type,
                "currency": "USD",
                "status": LedgerAccountStatus.ACTIVE,
            },
        )


@pytest.fixture
def ledger_accounts(website):
    """Ensure the minimum ledger accounts exist for payment tests."""
    _ensure_ledger_accounts(website)


@pytest.fixture
def client_wallet(client_user, website, ledger_accounts):
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