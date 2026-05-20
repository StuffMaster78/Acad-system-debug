from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import Count, QuerySet, Sum

from wallets.constants import WalletStatus, WalletType
from wallets.models import Wallet


class WalletSelectors:
    """
    Read-only wallet queries for the canonical wallets app.

    Other apps should use this layer for wallet reads instead of reaching into
    client_wallet, writer_wallet, or the old wallet app tables.
    """

    @staticmethod
    def base_queryset() -> QuerySet[Wallet]:
        return Wallet.objects.select_related("website", "owner_user")

    @staticmethod
    def for_website(*, website: Any) -> QuerySet[Wallet]:
        return WalletSelectors.base_queryset().filter(website=website)

    @staticmethod
    def active_for_website(*, website: Any) -> QuerySet[Wallet]:
        return WalletSelectors.for_website(website=website).filter(
            status=WalletStatus.ACTIVE,
        )

    @staticmethod
    def for_owner(
        *,
        website: Any,
        owner_user: Any,
        wallet_type: str | None = None,
        currency: str | None = None,
    ) -> QuerySet[Wallet]:
        queryset = WalletSelectors.for_website(website=website).filter(
            owner_user=owner_user,
        )

        if wallet_type:
            queryset = queryset.filter(wallet_type=wallet_type)

        if currency:
            queryset = queryset.filter(currency=currency)

        return queryset

    @staticmethod
    def get_owner_wallet(
        *,
        website: Any,
        owner_user: Any,
        wallet_type: str,
        currency: str = "USD",
    ) -> Wallet:
        return WalletSelectors.for_owner(
            website=website,
            owner_user=owner_user,
            wallet_type=wallet_type,
            currency=currency,
        ).get()

    @staticmethod
    def get_client_wallet(
        *,
        website: Any,
        client: Any,
        currency: str = "USD",
    ) -> Wallet:
        return WalletSelectors.get_owner_wallet(
            website=website,
            owner_user=client,
            wallet_type=WalletType.CLIENT,
            currency=currency,
        )

    @staticmethod
    def get_writer_wallet(
        *,
        website: Any,
        writer: Any,
        currency: str = "USD",
    ) -> Wallet:
        return WalletSelectors.get_owner_wallet(
            website=website,
            owner_user=writer,
            wallet_type=WalletType.WRITER,
            currency=currency,
        )

    @staticmethod
    def balances_for_owner(
        *,
        website: Any,
        owner_user: Any,
        currency: str = "USD",
    ) -> dict[str, Decimal]:
        wallets = WalletSelectors.for_owner(
            website=website,
            owner_user=owner_user,
            currency=currency,
        )

        return {
            wallet.wallet_type: wallet.available_balance
            for wallet in wallets
        }

    @staticmethod
    def summary_for_website(*, website: Any) -> dict[str, Any]:
        aggregate = WalletSelectors.for_website(website=website).aggregate(
            wallet_count=Count("id"),
            available_total=Sum("available_balance"),
            pending_total=Sum("pending_balance"),
            credited_total=Sum("total_credited"),
            debited_total=Sum("total_debited"),
        )

        return {
            "website_id": getattr(website, "id", None),
            "wallet_count": aggregate["wallet_count"] or 0,
            "available_total": aggregate["available_total"] or Decimal("0.00"),
            "pending_total": aggregate["pending_total"] or Decimal("0.00"),
            "credited_total": aggregate["credited_total"] or Decimal("0.00"),
            "debited_total": aggregate["debited_total"] or Decimal("0.00"),
        }
