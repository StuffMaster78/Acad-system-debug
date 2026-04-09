from __future__ import annotations

from typing import Any

from django.db import transaction

from ledger.constants import (
    LedgerAccountStatus,
    SYSTEM_ACCOUNT_CODES,
)
from ledger.models.ledger_account import LedgerAccount


class AccountService:
    """
    Handles creation and lookup of ledger accounts.
    """

    @staticmethod
    def get_account_by_code(*, website, code: str) -> LedgerAccount:
        return LedgerAccount.objects.get(
            website=website,
            code=code,
            status=LedgerAccountStatus.ACTIVE,
        )

    @staticmethod
    def get_system_account(*, website, key: str) -> LedgerAccount:
        code = SYSTEM_ACCOUNT_CODES[key]
        return AccountService.get_account_by_code(website=website, code=code)

    @staticmethod
    @transaction.atomic
    def create_account(
        *,
        website,
        code: str,
        name: str,
        account_type: str,
        currency: str = "KES",
        is_system_account: bool = False,
        allows_negative: bool = False,
        description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> LedgerAccount:
        return LedgerAccount.objects.create(
            website=website,
            code=code,
            name=name,
            account_type=account_type,
            currency=currency,
            is_system_account=is_system_account,
            allows_negative=allows_negative,
            description=description,
            metadata=metadata or {},
        )

    @staticmethod
    @transaction.atomic
    def get_or_create_account(
        *,
        website,
        code: str,
        defaults: dict[str, Any],
    ) -> tuple[LedgerAccount, bool]:
        return LedgerAccount.objects.get_or_create(
            website=website,
            code=code,
            defaults=defaults,
        )