from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from wallets.models import Wallet, WalletEntry


class WalletEntrySelectors:
    """
    Read-only wallet ledger entry queries.
    """

    @staticmethod
    def base_queryset() -> QuerySet[WalletEntry]:
        return WalletEntry.objects.select_related(
            "website",
            "wallet",
            "wallet__owner_user",
            "created_by",
            "ledger_transaction",
        )

    @staticmethod
    def for_website(*, website: Any) -> QuerySet[WalletEntry]:
        return WalletEntrySelectors.base_queryset().filter(website=website)

    @staticmethod
    def for_wallet(*, wallet: Wallet) -> QuerySet[WalletEntry]:
        return WalletEntrySelectors.for_website(website=wallet.website).filter(
            wallet=wallet,
        )

    @staticmethod
    def for_owner(
        *,
        website: Any,
        owner_user: Any,
        wallet_type: str | None = None,
        currency: str | None = None,
    ) -> QuerySet[WalletEntry]:
        queryset = WalletEntrySelectors.for_website(website=website).filter(
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
    ) -> QuerySet[WalletEntry]:
        return WalletEntrySelectors.for_website(website=website).filter(
            reference_type=reference_type,
            reference_id=str(reference_id),
        )
