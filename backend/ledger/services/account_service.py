from __future__ import annotations

from typing import Any

from django.db import transaction
from django.db.utils import IntegrityError

from ledger.constants import LedgerAccountStatus, SYSTEM_ACCOUNT_CODES
from ledger.models.ledger_account import LedgerAccount


class AccountService:
    """
    Handle tenant-scoped ledger account creation and lookup.

    Rules:
        1. Every lookup is scoped by website.
        2. Active account lookup only returns active accounts.
        3. System accounts are resolved through symbolic keys.
        4. Creation validates the model before saving.
    """

    @staticmethod
    def get_account_by_code(*, website: Any, code: str) -> LedgerAccount:
        """
        Return an active ledger account by tenant and account code.
        """
        return LedgerAccount.objects.get(
            website=website,
            code=code,
            status=LedgerAccountStatus.ACTIVE,
        )

    @staticmethod
    def get_system_account(*, website: Any, key: str) -> LedgerAccount:
        """
        Return a configured active system account by symbolic key.
        """
        code = SYSTEM_ACCOUNT_CODES.get(key)

        if not code:
            raise KeyError(f"Unknown system account key: {key}")

        return AccountService.get_account_by_code(
            website=website,
            code=code,
        )

    @staticmethod
    @transaction.atomic
    def create_account(
        *,
        website: Any,
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
        Create and validate a tenant-scoped ledger account.
        """
        account = LedgerAccount(
            website=website,
            code=code,
            name=name,
            account_type=account_type,
            currency=currency,
            status=LedgerAccountStatus.ACTIVE,
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
        website: Any,
        code: str,
        defaults: dict[str, Any],
    ) -> tuple[LedgerAccount, bool]:
        """
        Return an existing tenant-scoped account or create it safely.

        This method is race-safe enough for normal seed/admin flows:
        if another process creates the account first, it fetches it.
        """
        try:
            return (
                LedgerAccount.objects.get(
                    website=website,
                    code=code,
                ),
                False,
            )
        except LedgerAccount.DoesNotExist:
            try:
                account = AccountService.create_account(
                    website=website,
                    code=code,
                    name=defaults["name"],
                    account_type=defaults["account_type"],
                    currency=defaults.get("currency", "USD"),
                    is_system_account=defaults.get(
                        "is_system_account",
                        False,
                    ),
                    allows_negative=defaults.get("allows_negative", False),
                    description=defaults.get("description", ""),
                    metadata=defaults.get("metadata"),
                )
                return account, True
            except IntegrityError:
                return (
                    LedgerAccount.objects.get(
                        website=website,
                        code=code,
                    ),
                    False,
                )