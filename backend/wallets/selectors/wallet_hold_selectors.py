from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from wallets.constants import WalletHoldStatus
from wallets.models import Wallet, WalletHold


class WalletHoldSelectors:
    """
    Read-only wallet hold queries for checkout and payout reservations.
    """

    @staticmethod
    def base_queryset() -> QuerySet[WalletHold]:
        return WalletHold.objects.select_related(
            "website",
            "wallet",
            "wallet__owner_user",
            "created_by",
        )

    @staticmethod
    def for_website(*, website: Any) -> QuerySet[WalletHold]:
        return WalletHoldSelectors.base_queryset().filter(website=website)

    @staticmethod
    def active_for_website(*, website: Any) -> QuerySet[WalletHold]:
        return WalletHoldSelectors.for_website(website=website).filter(
            status=WalletHoldStatus.ACTIVE,
        )

    @staticmethod
    def for_wallet(*, wallet: Wallet) -> QuerySet[WalletHold]:
        return WalletHoldSelectors.for_website(website=wallet.website).filter(
            wallet=wallet,
        )

    @staticmethod
    def active_for_wallet(*, wallet: Wallet) -> QuerySet[WalletHold]:
        return WalletHoldSelectors.for_wallet(wallet=wallet).filter(
            status=WalletHoldStatus.ACTIVE,
        )

    @staticmethod
    def for_owner(
        *,
        website: Any,
        owner_user: Any,
        wallet_type: str | None = None,
        currency: str | None = None,
    ) -> QuerySet[WalletHold]:
        queryset = WalletHoldSelectors.for_website(website=website).filter(
            wallet__owner_user=owner_user,
        )

        if wallet_type:
            queryset = queryset.filter(wallet__wallet_type=wallet_type)

        if currency:
            queryset = queryset.filter(wallet__currency=currency)

        return queryset

    @staticmethod
    def by_reference(
        *,
        website: Any,
        reference_type: str,
        reference_id: str,
    ) -> QuerySet[WalletHold]:
        return WalletHoldSelectors.for_website(website=website).filter(
            reference_type=reference_type,
            reference_id=str(reference_id),
        )
