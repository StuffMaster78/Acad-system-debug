from __future__ import annotations

from django.db.models import QuerySet

from ledger.constants import LedgerAccountStatus
from ledger.models.ledger_account import LedgerAccount


class LedgerAccountSelectors:
    """
    Read only queries for ledger accounts.
    """

    @staticmethod
    def get_accounts_for_website(*, website) -> QuerySet[LedgerAccount]:
        return LedgerAccount.objects.filter(
            website=website
        ).order_by("account_type", "code")

    @staticmethod
    def get_active_accounts_for_website(*, website) -> QuerySet[LedgerAccount]:
        return LedgerAccount.objects.filter(
            website=website,
            status=LedgerAccountStatus.ACTIVE,
        ).order_by("account_type", "code")

    @staticmethod
    def get_account_by_code(
        *,
        website,
        code: str,
    ) -> LedgerAccount:
        return LedgerAccount.objects.get(
            website=website,
            code=code,
        )

    @staticmethod
    def get_system_accounts_for_website(*, website) -> QuerySet[LedgerAccount]:
        return LedgerAccount.objects.filter(
            website=website,
            is_system_account=True,
        ).order_by("account_type", "code")

    @staticmethod
    def get_accounts_by_type(
        *,
        website,
        account_type: str,
    ) -> QuerySet[LedgerAccount]:
        return LedgerAccount.objects.filter(
            website=website,
            account_type=account_type,
        ).order_by("code")