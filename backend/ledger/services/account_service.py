from __future__ import annotations

from typing import Any

from django.db import transaction

from ledger.constants import LedgerAccountStatus, SYSTEM_ACCOUNT_CODES
from ledger.models.ledger_account import LedgerAccount


class AccountService:
    """
    Handle creation and lookup of ledger accounts.
    """

    @staticmethod
    def get_account_by_code(*, website, code: str) -> LedgerAccount:
        """
        Return an active ledger account by tenant and code.
        """
        return LedgerAccount.objects.get(
            website=website,
            code=code,
            status=LedgerAccountStatus.ACTIVE,
        )

    @staticmethod
    def get_system_account(*, website, key: str) -> LedgerAccount:
        """
        Return a configured system account by symbolic key.
        """
        try:
            code = SYSTEM_ACCOUNT_CODES[key]
        except KeyError as exc:
            raise KeyError(
                f"Unknown system account key: {key}"
            ) from exc

        return AccountService.get_account_by_code(
            website=website,
            code=code,
        )

    @staticmethod
    @transaction.atomic
    def create_account(
        *,
        website,
        code: str,
        name: str,
        account_type: str,
        currency: str = "USD",
        is_system_account: bool = False,
        allows_negative: bool = False,
        description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> LedgerAccount:
        """
        Create and validate a ledger account.
        """
        account = LedgerAccount(
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
        account.full_clean()
        account.save()
        return account

    @staticmethod
    @transaction.atomic
    def get_or_create_account(
        *,
        website,
        code: str,
        defaults: dict[str, Any],
    ) -> tuple[LedgerAccount, bool]:
        try:
            account = LedgerAccount.objects.get(
                website=website,
                code=code,
            )
            return account, False
        except LedgerAccount.DoesNotExist:
            account = AccountService.create_account(
                website=website,
                code=code,
                name=defaults["name"],
                account_type=defaults["account_type"],
                currency=defaults.get("currency", "USD"),
                is_system_account=defaults.get("is_system_account", False),
                allows_negative=defaults.get("allows_negative", False),
                description=defaults.get("description", ""),
                metadata=defaults.get("metadata"),
            )
            return account, True