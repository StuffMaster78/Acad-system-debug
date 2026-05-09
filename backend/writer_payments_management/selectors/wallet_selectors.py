from __future__ import annotations

from django.db.models import QuerySet

from wallets.models.wallet import Wallet


class WalletSelectors:
    """
    Read-only wallet query layer.

    IMPORTANT:
        No balance mutation logic here.
    """

    @staticmethod
    def base_queryset() -> QuerySet:
        return Wallet.objects.select_related(
            "website",
            "owner_user",
        )

    @staticmethod
    def by_owner(*, website, owner_user) -> QuerySet:
        return WalletSelectors.base_queryset().filter(
            website=website,
            owner_user=owner_user,
        )

    @staticmethod
    def writer_wallet(*, website, owner_user) -> Wallet:
        return WalletSelectors.by_owner(
            website=website,
            owner_user=owner_user,
        ).get(wallet_type="WRITER")

    @staticmethod
    def client_wallet(*, website, owner_user) -> Wallet:
        return WalletSelectors.by_owner(
            website=website,
            owner_user=owner_user,
        ).get(wallet_type="CLIENT")