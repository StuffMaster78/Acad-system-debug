from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from django.db.models import Count, Sum
from django.utils import timezone

from ledger.constants import EntrySide, JournalEntryStatus
from ledger.models import JournalEntry, JournalLine


@dataclass(frozen=True)
class ReconciliationIssue:
    """
    Single ledger reconciliation issue.
    """

    code: str
    message: str
    severity: str
    journal_entry_id: str = ""
    entry_number: str = ""
    reference: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReconciliationReport:
    """
    Result of a ledger reconciliation run.
    """

    website_id: str
    checked_at: Any
    issues: list[ReconciliationIssue]

    @property
    def has_issues(self) -> bool:
        """
        Return True when reconciliation found issues.
        """
        return bool(self.issues)


class LedgerReconciliationService:
    """
    Read-only ledger audit and reconciliation service.

    This service does not mutate money records. It only detects issues.
    """

    SEVERITY_LOW = "low"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_HIGH = "high"
    SEVERITY_CRITICAL = "critical"

    @classmethod
    def reconcile_website(cls, *, website) -> ReconciliationReport:
        """
        Run all ledger reconciliation checks for one tenant.
        """
        issues: list[ReconciliationIssue] = []

        issues.extend(
            cls.find_unbalanced_posted_entries(
                website=website,
            )
        )
        issues.extend(
            cls.find_entries_without_lines(
                website=website,
            )
        )
        issues.extend(
            cls.find_lines_with_wrong_tenant(
                website=website,
            )
        )
        issues.extend(
            cls.find_lines_with_wrong_currency(
                website=website,
            )
        )
        issues.extend(
            cls.find_duplicate_references(
                website=website,
            )
        )
        issues.extend(
            cls.find_posted_entries_missing_reference(
                website=website,
            )
        )
        issues.extend(
            cls.find_stale_draft_entries(
                website=website,
            )
        )

        return ReconciliationReport(
            website_id=str(website.id),
            checked_at=timezone.now(),
            issues=issues,
        )

    @classmethod
    def find_unbalanced_posted_entries(
        cls,
        *,
        website,
    ) -> list[ReconciliationIssue]:
        """
        Find posted entries whose debit and credit totals do not match.

        This should never happen if entries are posted only through
        JournalPostingService, but this check protects against manual DB
        edits, old migrations, or legacy imports.
        """
        issues: list[ReconciliationIssue] = []

        entries = JournalEntry.objects.filter(
            website=website,
            status=JournalEntryStatus.POSTED,
        ).only(
            "id",
            "entry_number",
            "reference",
        )

        for entry in entries:
            debit_total = (
                JournalLine.objects.filter(
                    website=website,
                    journal_entry=entry,
                    entry_side=EntrySide.DEBIT,
                ).aggregate(total=Sum("amount"))["total"]
                or Decimal("0.00")
            )

            credit_total = (
                JournalLine.objects.filter(
                    website=website,
                    journal_entry=entry,
                    entry_side=EntrySide.CREDIT,
                ).aggregate(total=Sum("amount"))["total"]
                or Decimal("0.00")
            )

            if debit_total != credit_total:
                issues.append(
                    ReconciliationIssue(
                        code="UNBALANCED_POSTED_ENTRY",
                        message=(
                            "Posted journal entry is unbalanced. "
                            f"Debits={debit_total}, "
                            f"Credits={credit_total}."
                        ),
                        severity=cls.SEVERITY_CRITICAL,
                        journal_entry_id=str(entry.id),
                        entry_number=entry.entry_number,
                        reference=entry.reference,
                        metadata={
                            "debit_total": str(debit_total),
                            "credit_total": str(credit_total),
                        },
                    )
                )

        return issues

    @classmethod
    def find_entries_without_lines(
        cls,
        *,
        website,
    ) -> list[ReconciliationIssue]:
        """
        Find journal entries that have no journal lines.
        """
        issues: list[ReconciliationIssue] = []

        entries = JournalEntry.objects.filter(
            website=website,
        ).annotate(
            line_count=Count("lines"),
        ).filter(
            line_count=0,
        ).only(
            "id",
            "entry_number",
            "reference",
            "status",
        )

        for entry in entries:
            issues.append(
                ReconciliationIssue(
                    code="ENTRY_WITHOUT_LINES",
                    message="Journal entry has no journal lines.",
                    severity=cls.SEVERITY_HIGH,
                    journal_entry_id=str(entry.id),
                    entry_number=entry.entry_number,
                    reference=entry.reference,
                    metadata={
                        "status": entry.status,
                    },
                )
            )

        return issues

    @classmethod
    def find_lines_with_wrong_tenant(
        cls,
        *,
        website,
    ) -> list[ReconciliationIssue]:
        """
        Find journal lines whose account belongs to another tenant.
        """
        issues: list[ReconciliationIssue] = []

        lines = JournalLine.objects.select_related(
            "journal_entry",
            "ledger_account",
        ).filter(
            website=website,
        ).exclude(
            ledger_account__website=website,
        )

        for line in lines:
            issues.append(
                ReconciliationIssue(
                    code="LINE_ACCOUNT_TENANT_MISMATCH",
                    message=(
                        "Journal line uses a ledger account from "
                        "another website."
                    ),
                    severity=cls.SEVERITY_CRITICAL,
                    journal_entry_id=str(line.journal_entry.id),
                    entry_number=line.journal_entry.entry_number,
                    reference=line.journal_entry.reference,
                    metadata={
                        "line_id": str(line.id),
                        "line_website_id": str(line.website.id),
                        "account_id": str(line.ledger_account.id),
                        "account_website_id": str(
                            line.ledger_account.website_id,
                        ),
                    },
                )
            )

        return issues

    @classmethod
    def find_lines_with_wrong_currency(
        cls,
        *,
        website,
    ) -> list[ReconciliationIssue]:
        """
        Find journal lines whose account currency differs from entry currency.
        """
        issues: list[ReconciliationIssue] = []

        lines = JournalLine.objects.select_related(
            "journal_entry",
            "ledger_account",
        ).filter(
            website=website,
        ).exclude(
            ledger_account__currency__exact="",
        )

        for line in lines:
            entry_currency = line.journal_entry.currency
            account_currency = line.ledger_account.currency

            if entry_currency == account_currency:
                continue

            issues.append(
                ReconciliationIssue(
                    code="LINE_ACCOUNT_CURRENCY_MISMATCH",
                    message=(
                        "Journal line account currency does not match "
                        "journal entry currency."
                    ),
                    severity=cls.SEVERITY_HIGH,
                    journal_entry_id=str(line.journal_entry.id),
                    entry_number=line.journal_entry.entry_number,
                    reference=line.journal_entry.reference,
                    metadata={
                        "line_id": str(line.id),
                        "entry_currency": entry_currency,
                        "account_currency": account_currency,
                    },
                )
            )

        return issues

    @classmethod
    def find_duplicate_references(
        cls,
        *,
        website,
    ) -> list[ReconciliationIssue]:
        """
        Find duplicate posted journal entry references.

        Blank references are ignored because some manual entries may not have
        external references.
        """
        issues: list[ReconciliationIssue] = []

        duplicates = (
            JournalEntry.objects.filter(
                website=website,
                status=JournalEntryStatus.POSTED,
            )
            .exclude(reference="")
            .values("reference", "entry_type")
            .annotate(entry_count=Count("id"))
            .filter(entry_count__gt=1)
        )

        for duplicate in duplicates:
            issues.append(
                ReconciliationIssue(
                    code="DUPLICATE_POSTED_REFERENCE",
                    message=(
                        "Multiple posted journal entries share the same "
                        "reference and entry type."
                    ),
                    severity=cls.SEVERITY_HIGH,
                    reference=duplicate["reference"],
                    metadata={
                        "entry_type": duplicate["entry_type"],
                        "entry_count": duplicate["entry_count"],
                    },
                )
            )

        return issues

    @classmethod
    def find_posted_entries_missing_reference(
        cls,
        *,
        website,
    ) -> list[ReconciliationIssue]:
        """
        Find posted entries missing useful trace references.
        """
        issues: list[ReconciliationIssue] = []

        entries = JournalEntry.objects.filter(
            website=website,
            status=JournalEntryStatus.POSTED,
            reference="",
        ).only(
            "id",
            "entry_number",
            "entry_type",
            "reference",
            "source_app",
            "source_model",
            "source_object_id",
        )

        for entry in entries:
            issues.append(
                ReconciliationIssue(
                    code="POSTED_ENTRY_MISSING_REFERENCE",
                    message="Posted journal entry has no reference.",
                    severity=cls.SEVERITY_MEDIUM,
                    journal_entry_id=str(entry.id),
                    entry_number=entry.entry_number,
                    reference=entry.reference,
                    metadata={
                        "entry_type": entry.entry_type,
                        "source_app": entry.source_app,
                        "source_model": entry.source_model,
                        "source_object_id": entry.source_object_id,
                    },
                )
            )

        return issues

    @classmethod
    def find_stale_draft_entries(
        cls,
        *,
        website,
        older_than_hours: int = 24,
    ) -> list[ReconciliationIssue]:
        """
        Find draft entries that have stayed unposted for too long.
        """
        issues: list[ReconciliationIssue] = []

        cutoff = timezone.now() - timezone.timedelta(
            hours=older_than_hours,
        )

        entries = JournalEntry.objects.filter(
            website=website,
            status=JournalEntryStatus.DRAFT,
            created_at__lt=cutoff,
        ).only(
            "id",
            "entry_number",
            "reference",
            "entry_type",
            "created_at",
        )

        for entry in entries:
            issues.append(
                ReconciliationIssue(
                    code="STALE_DRAFT_ENTRY",
                    message=(
                        "Draft journal entry has remained unposted "
                        "beyond the allowed age."
                    ),
                    severity=cls.SEVERITY_MEDIUM,
                    journal_entry_id=str(entry.id),
                    entry_number=entry.entry_number,
                    reference=entry.reference,
                    metadata={
                        "entry_type": entry.entry_type,
                        "created_at": entry.created_at.isoformat(),
                        "older_than_hours": older_than_hours,
                    },
                )
            )

        return issues