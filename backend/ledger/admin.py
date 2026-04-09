from django.contrib import admin

from ledger.models import (
    AccountBalanceSnapshot,
    HoldRecord,
    JournalEntry,
    JournalLine,
    LedgerAccount,
    ReconciliationRecord,
)


@admin.register(LedgerAccount)
class LedgerAccountAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "website",
        "account_type",
        "currency",
        "status",
        "is_system_account",
        "allows_negative",
        "created_at",
    )
    list_filter = (
        "account_type",
        "currency",
        "status",
        "is_system_account",
        "allows_negative",
        "website",
    )
    search_fields = (
        "code",
        "name",
        "description",
        "website__name",
        "website__domain",
    )
    ordering = ("website", "account_type", "code")
    readonly_fields = ("id", "created_at", "updated_at")


class JournalLineInline(admin.TabularInline):
    model = JournalLine
    extra = 0
    readonly_fields = ("id", "created_at", "updated_at")
    fields = (
        "ledger_account",
        "entry_side",
        "amount",
        "currency",
        "description",
        "user",
        "wallet_reference",
        "payment_intent_reference",
        "related_object_type",
        "related_object_id",
        "metadata",
    )
    show_change_link = True


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = (
        "entry_number",
        "entry_type",
        "status",
        "website",
        "currency",
        "reference",
        "source_model",
        "source_object_id",
        "external_reference",
        "payment_intent_reference",
        "posted_at",
        "created_at",
    )
    list_filter = (
        "entry_type",
        "status",
        "currency",
        "source_app",
        "website",
    )
    search_fields = (
        "entry_number",
        "reference",
        "source_model",
        "source_object_id",
        "external_reference",
        "payment_intent_reference",
        "description",
    )
    ordering = ("-created_at",)
    readonly_fields = (
        "id",
        "entry_number",
        "posted_at",
        "created_at",
        "updated_at",
    )
    inlines = [JournalLineInline]


@admin.register(JournalLine)
class JournalLineAdmin(admin.ModelAdmin):
    list_display = (
        "journal_entry",
        "ledger_account",
        "entry_side",
        "amount",
        "currency",
        "website",
        "wallet_reference",
        "payment_intent_reference",
        "related_object_type",
        "related_object_id",
        "created_at",
    )
    list_filter = (
        "entry_side",
        "currency",
        "website",
        "ledger_account",
    )
    search_fields = (
        "journal_entry__entry_number",
        "ledger_account__code",
        "ledger_account__name",
        "wallet_reference",
        "payment_intent_reference",
        "related_object_type",
        "related_object_id",
        "description",
    )
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(HoldRecord)
class HoldRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "ledger_account",
        "user",
        "amount",
        "currency",
        "status",
        "reference",
        "wallet_reference",
        "payment_intent_reference",
        "expires_at",
        "created_at",
    )
    list_filter = (
        "status",
        "currency",
        "website",
        "ledger_account",
    )
    search_fields = (
        "reference",
        "reason",
        "wallet_reference",
        "payment_intent_reference",
        "related_object_type",
        "related_object_id",
    )
    ordering = ("-created_at",)
    readonly_fields = (
        "id",
        "captured_at",
        "released_at",
        "cancelled_at",
        "created_at",
        "updated_at",
    )


@admin.register(ReconciliationRecord)
class ReconciliationRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "status",
        "currency",
        "expected_amount",
        "actual_amount",
        "matched_amount",
        "variance_amount",
        "reference",
        "external_reference",
        "payment_intent_reference",
        "reconciled_at",
        "resolved_at",
        "created_at",
    )
    list_filter = (
        "status",
        "currency",
        "website",
        "source_app",
    )
    search_fields = (
        "reference",
        "external_reference",
        "payment_intent_reference",
        "source_model",
        "source_object_id",
        "mismatch_reason",
    )
    ordering = ("-created_at",)
    readonly_fields = (
        "id",
        "reconciled_at",
        "resolved_at",
        "created_at",
        "updated_at",
    )


@admin.register(AccountBalanceSnapshot)
class AccountBalanceSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "ledger_account",
        "website",
        "currency",
        "balance",
        "reference",
        "snapshot_date",
        "created_at",
    )
    list_filter = (
        "currency",
        "website",
        "ledger_account",
    )
    search_fields = (
        "ledger_account__code",
        "ledger_account__name",
        "reference",
    )
    ordering = ("-snapshot_date",)
    readonly_fields = ("id", "created_at")