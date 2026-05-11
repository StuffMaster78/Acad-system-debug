from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from tips.enums.tip_status import TipStatus
from tips.models.tip import Tip
from tips.services.tip_split_calculator import TipSplitCalculator

from ledger.constants import EntrySide, LedgerEntryType, SourceApp
from ledger.services.account_service import AccountService
from ledger.services.journal_posting_service import (
    JournalLineInput,
    JournalPostingService,
)

from audit_logging.services.audit_service import AuditService


class TipSettlementEngine:
    """
    Converts SUCCEEDED tips into ledger truth.

    HARD RULES:
    - Idempotent (row lock)
    - Only SUCCEEDED tips
    - Ledger is SOURCE OF TRUTH
    - No external side effects
    """

    @staticmethod
    @transaction.atomic
    def settle_tip(*, tip: Tip, triggered_by=None) -> Tip:

        tip = (
            Tip.objects.select_for_update()
            .select_related("receiver__wallet")
            .get(id=tip.pk)
        )

        if tip.status != TipStatus.SUCCEEDED:
            return tip

        if tip.is_settled:
            return tip

        split = TipSplitCalculator.calculate(
            policy=tip.active_policy,
            gross_amount=tip.gross_amount,
        )

        writer_amount = split["writer_amount"]
        platform_amount = split["platform_amount"]

        TipSettlementEngine._write_ledger_entries(
            website=tip.sender.website,
            tip=tip,
            writer_amount=writer_amount,
            platform_amount=platform_amount,
            triggered_by=triggered_by,
        )

        tip.is_settled = True
        tip.settled_at = timezone.now()
        tip.save(update_fields=["is_settled", "settled_at"])

        AuditService.record(
            action="tip.settled",
            actor=triggered_by,
            obj=tip,
            website=getattr(tip.sender, "website", None),
            metadata={
                "tip_id": tip.pk,
                "writer_amount": str(writer_amount),
                "platform_amount": str(platform_amount),
            },
        )

        return tip

    # ------------------------------------------------------------ #
    # LEDGER CORE
    # ------------------------------------------------------------ #

    @staticmethod
    def _write_ledger_entries(
        *,
        website,
        tip: Tip,
        writer_amount,
        platform_amount,
        triggered_by=None,
    ) -> None:

        writer_wallet = tip.receiver.wallet

        writer_account = AccountService.get_system_account(
            website=website,
            key="writer_earnings",
        )

        platform_account = AccountService.get_system_account(
            website=website,
            key="platform_revenue",
        )

        clearing_account = AccountService.get_system_account(
            website=website,
            key="tip_allocation_clearing",
        )

        JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.TIP_SETTLEMENT,
            lines=[
                JournalLineInput(
                    ledger_account=clearing_account,
                    entry_side=EntrySide.DEBIT,
                    amount=tip.gross_amount,
                    description="Clear tip allocation",
                    related_object_type="Tip",
                    related_object_id=str(tip.pk),
                ),
                JournalLineInput(
                    ledger_account=writer_account,
                    entry_side=EntrySide.CREDIT,
                    amount=writer_amount,
                    description="Writer earnings from tip",
                    related_object_type="Tip",
                    related_object_id=str(tip.pk),
                ),
                JournalLineInput(
                    ledger_account=platform_account,
                    entry_side=EntrySide.CREDIT,
                    amount=platform_amount,
                    description="Platform fee from tip",
                    related_object_type="Tip",
                    related_object_id=str(tip.pk),
                ),
            ],
            currency="USD",
            description="Tip settlement",
            reference=str(tip.pk),
            source_app=SourceApp.TIPS,
            source_model="Tip",
            source_object_id=str(tip.pk),
            triggered_by=triggered_by,
            metadata={
                "tip_id": str(tip.pk),
            },
        )