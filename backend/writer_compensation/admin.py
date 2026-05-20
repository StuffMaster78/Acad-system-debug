"""
writer_compensation/admin.py

Comprehensive Django admin covering all models:
  PaymentWindow, CompensationEvent, PayoutBatch, PayoutRecord,
  WriterPayoutPreference, PaymentWindowChangeRequest,
  CompensationAdjustment, AdvancePaymentRequest, AdvanceRecovery,
  DeferredSettlementItem, CorrectionEvent, WriterBalanceSnapshot,
  PayoutClearance, ReversalChain, ExposureLedger,
  PayoutReconciliationReport, IdempotencyRecord, OutboxEvent

Fixes vs previous version:
  - PayoutItemStatus → PayoutRecordStatus (unified enum)
  - window= → payment_window= throughout
  - window_type → cycle_type on PaymentWindow and WriterPayoutPreference
  - batch.items → batch.records
  - CompensationEvent list_display "window" → "payment_window"
  - CompensationEvent list_filter "window__website" → "payment_window__website"
  - PayoutBatch list_filter "window__status" → "payment_window__status"
  - PayoutClearance FK app label: writer_payments_management → writer_compensation
  - All models now registered and covered
"""

from __future__ import annotations

from decimal import Decimal

from django.contrib import admin
from django.db.models import Count, Sum
from django.utils.html import format_html

from writer_compensation.enums.compensation_enums import (
    AdvancePaymentStatus,
    EventStatus,
    PayoutBatchStatus,
    PayoutRecordStatus,
    WindowStatus,
)
from writer_compensation.models.adjustment import CompensationAdjustment
from writer_compensation.models.advance_payment import (
    AdvancePaymentRequest,
    AdvanceRecovery,
)
from writer_compensation.models.compensation_event import CompensationEvent
from writer_compensation.models.correction_event import CorrectionEvent
from writer_compensation.models.cycle_change_request import PaymentWindowChangeRequest
from writer_compensation.models.deferred_settlement import DeferredSettlementItem
from writer_compensation.models.exposure_ledger import ExposureLedger
from writer_compensation.models.idempotency_models import IdempotencyRecord
from writer_compensation.models.outbox_event_models import OutboxEvent
from writer_compensation.models.payment_window import PaymentWindow
from writer_compensation.models.payout_batch import PayoutBatch
from writer_compensation.models.payout_clearance import PayoutClearance
from writer_compensation.models.payout_reconciliation_report import (
    PayoutReconciliationReport,
)
from writer_compensation.models.payout_record import PayoutRecord
from writer_compensation.models.reversal_chain import ReversalChain
from writer_compensation.models.writer_balance_snapshot import WriterBalanceSnapshot
from writer_compensation.models.writer_payout_preference import WriterPayoutPreference
from writer_compensation.services.payout_engine_service import PayoutEngineService
from writer_compensation.services.window_service import WindowService


# ===========================================================================
# SHARED HELPERS
# ===========================================================================

_STATUS_COLOURS: dict[str, tuple[str, str]] = {
    # Window
    WindowStatus.UPCOMING:   ("5C6BC0", "white"),
    WindowStatus.OPEN:       ("1B6AAA", "white"),
    WindowStatus.CLOSED:     ("8B5E0A", "white"),
    WindowStatus.PROCESSING: ("0E6B74", "white"),
    WindowStatus.DONE:       ("1A5C2A", "white"),
    # Payout record
    PayoutRecordStatus.PENDING:   ("8B5E0A", "white"),
    PayoutRecordStatus.CONFIRMED: ("1B6AAA", "white"),
    PayoutRecordStatus.PAID:      ("1A5C2A", "white"),
    PayoutRecordStatus.HELD:      ("B84232", "white"),
    PayoutRecordStatus.DEFERRED:  ("5C6BC0", "white"),
    PayoutRecordStatus.FAILED:    ("8B0000", "white"),
    # Advance
    AdvancePaymentStatus.PENDING:             ("8B5E0A", "white"),
    AdvancePaymentStatus.APPROVED:            ("1B6AAA", "white"),
    AdvancePaymentStatus.REJECTED:            ("B84232", "white"),
    AdvancePaymentStatus.RECOVERED:           ("1A5C2A", "white"),
    AdvancePaymentStatus.PARTIALLY_RECOVERED: ("0E6B74", "white"),
    # Event
    EventStatus.PENDING_CONFIRMATION:   ("8B5E0A",  "white"),
    EventStatus.MATURED:                ("1B6AAA",  "white"),
    EventStatus.INCLUDED_IN_SETTLEMENT: ("0E6B74",  "white"),
    EventStatus.PAID:                   ("1A5C2A",  "white"),
    EventStatus.REVERSED:               ("B84232",  "white"),
    EventStatus.VOIDED:                 ("555555",  "white"),
    EventStatus.DISPUTED:               ("8B0000",  "white"),
    EventStatus.ON_HOLD:                ("8B5E0A",  "white"),
    EventStatus.DEFERRED:               ("5C6BC0",  "white"),
    # Outbox
    "PENDING":    ("8B5E0A", "white"),
    "PROCESSING": ("1B6AAA", "white"),
    "DONE":       ("1A5C2A", "white"),
    "DEAD":       ("8B0000", "white"),
    # Correction
    "OPEN":     ("8B5E0A", "white"),
    "RESOLVED": ("1A5C2A", "white"),
}


def badge(label: str) -> str:
    bg, fg = _STATUS_COLOURS.get(label, ("777777", "white"))
    return format_html(
        '<span style="background:#{};color:{};padding:2px 9px;'
        'border-radius:4px;font-size:11px;font-weight:500">{}</span>',
        bg, fg, label,
    )


def amount_html(value, positive_is_green: bool = True) -> str:
    try:
        d = Decimal(str(value))
    except Exception:
        return str(value)
    colour = (
        "green" if (d > 0 and positive_is_green) or (d < 0 and not positive_is_green)
        else "red"
    )
    return format_html(
        '<span style="color:{};font-weight:500">{}</span>',
        colour, d,
    )


# ===========================================================================
# INLINES
# ===========================================================================

class CompensationEventInline(admin.TabularInline):
    model            = CompensationEvent
    extra            = 0
    can_delete       = False
    show_change_link = True
    fields           = ("event_type", "amount", "status", "source_type", "source_id", "created_at")
    readonly_fields  = fields


class PayoutRecordInline(admin.TabularInline):
    model            = PayoutRecord
    extra            = 0
    can_delete       = False
    show_change_link = True
    fields           = ("writer", "total_amount", "status", "confirmed_at", "paid_at")
    readonly_fields  = fields


class AdvanceRecoveryInline(admin.TabularInline):
    model            = AdvanceRecovery
    extra            = 0
    can_delete       = False
    show_change_link = True
    fields           = ("amount", "settlement_period", "notes", "recovered_at")
    readonly_fields  = fields


class PayoutClearanceInline(admin.TabularInline):
    model            = PayoutClearance
    extra            = 0
    can_delete       = False
    show_change_link = True
    fields           = ("amount_sent", "method", "external_reference", "status", "processed_at")
    readonly_fields  = fields


class DeferredSettlementItemInline(admin.TabularInline):
    model            = DeferredSettlementItem
    extra            = 0
    can_delete       = False
    show_change_link = True
    fk_name          = "from_payment_window"
    fields           = ("financial_event", "to_payment_window", "reason", "deferred_by", "created_at")
    readonly_fields  = fields


# ===========================================================================
# PAYMENT WINDOW
# ===========================================================================

@admin.register(PaymentWindow)
class PaymentWindowAdmin(admin.ModelAdmin):
    list_display = (
        "id", "website", "cycle_type",
        "start_date", "end_date",
        "window_status", "event_count",
        "pending_events", "created_at",
    )
    list_filter  = ("status", "cycle_type", "website")
    search_fields = ("website__name", "title")
    readonly_fields = (
        "status", "closed_at", "processing_at",
        "done_at", "created_at", "updated_at",
    )
    ordering            = ("-start_date",)
    list_select_related = ("website",)
    date_hierarchy      = "created_at"
    inlines             = (CompensationEventInline, DeferredSettlementItemInline)
    actions             = ("action_close", "action_start_processing", "action_mark_done")

    fieldsets = (
        ("Window info", {
            "fields": ("website", "title", "cycle_type", "start_date", "end_date"),
        }),
        ("Status", {
            "fields": ("status", "locked", "closed_at", "processing_at", "done_at"),
        }),
        ("Advance settings", {
            "fields": (
                "allow_advances", "advance_percentage_cap",
                "minimum_advance_amount",
            ),
        }),
        ("Audit", {
            "fields": ("created_by", "created_at", "updated_at"),
        }),
    )

    @admin.display(description="Status")
    def window_status(self, obj):
        return badge(obj.status)

    @admin.display(description="Events")
    def event_count(self, obj):
        return CompensationEvent.objects.filter(payment_window=obj).count()

    @admin.display(description="Pending")
    def pending_events(self, obj):
        count = CompensationEvent.objects.filter(
            payment_window=obj,
            status=EventStatus.PENDING_CONFIRMATION,
        ).count()
        if count:
            return format_html(
                '<span style="color:#8B5E0A;font-weight:500">{}</span>', count,
            )
        return count

    @admin.action(description="Close selected windows (OPEN → CLOSED)")
    def action_close(self, request, queryset):
        for window in queryset.filter(status=WindowStatus.OPEN):
            try:
                WindowService.close_window(window, closed_by=request.user)
                self.message_user(request, f"Window {window.pk} closed.")
            except Exception as exc:
                self.message_user(request, f"Window {window.pk}: {exc}", level="error")

    @admin.action(description="Start processing (CLOSED → PROCESSING)")
    def action_start_processing(self, request, queryset):
        for window in queryset.filter(status=WindowStatus.CLOSED):
            try:
                WindowService.start_processing(window)
                self.message_user(request, f"Window {window.pk} → PROCESSING.")
            except Exception as exc:
                self.message_user(request, f"Window {window.pk}: {exc}", level="error")

    @admin.action(description="Mark done (PROCESSING → DONE)")
    def action_mark_done(self, request, queryset):
        for window in queryset.filter(status=WindowStatus.PROCESSING):
            try:
                WindowService.mark_done(window)
                self.message_user(request, f"Window {window.pk} → DONE.")
            except Exception as exc:
                self.message_user(request, f"Window {window.pk}: {exc}", level="error")


# ===========================================================================
# COMPENSATION EVENT
# ===========================================================================

@admin.register(CompensationEvent)
class CompensationEventAdmin(admin.ModelAdmin):
    list_display = (
        "id", "writer", "event_type",
        "amount_display", "event_status",
        "source_type", "source_id",
        "payment_window", "created_at",
    )
    list_filter = (
        "event_type",
        "status",
        "payment_window__website",
    )
    search_fields = (
        "writer__account_profile__user__email",
        "writer__account_profile__user__first_name",
        "idempotency_key",
        "source_id",
        "reference",
    )
    readonly_fields = (
        "website", "writer", "payment_window",
        "related_window", "related_event",
        "event_type", "amount", "status",
        "source", "source_type", "source_id",
        "idempotency_key", "created_by",
        "created_at", "updated_at",
    )
    ordering            = ("-created_at",)
    list_select_related = ("writer__account_profile__user", "payment_window")
    date_hierarchy      = "created_at"

    fieldsets = (
        ("Event", {
            "fields": (
                "website", "writer", "payment_window", "related_window",
                "event_type", "source", "source_type", "source_id",
                "related_event",
            ),
        }),
        ("Financials", {
            "fields": ("amount", "currency", "status"),
        }),
        ("Metadata", {
            "fields": (
                "title", "description", "notes", "reference",
                "external_reference", "idempotency_key", "metadata",
            ),
        }),
        ("Flags", {
            "fields": (
                "is_visible_to_writer", "is_risky", "is_locked",
                "matured_at", "disputed_at", "reversed_at",
            ),
        }),
        ("Audit", {
            "fields": ("created_by", "created_at", "updated_at"),
        }),
    )

    @admin.display(description="Amount")
    def amount_display(self, obj):
        return format_html(amount_html(obj.amount))

    @admin.display(description="Status")
    def event_status(self, obj):
        return badge(obj.status)

    def has_add_permission(self, request):
        # Events are created only through services — never directly.
        return False

    def has_delete_permission(self, request, obj=None):
        # Events are immutable.
        return False


# ===========================================================================
# PAYOUT BATCH
# ===========================================================================

@admin.register(PayoutBatch)
class PayoutBatchAdmin(admin.ModelAdmin):
    list_display = (
        "id", "payment_window", "batch_status",
        "total_amount", "total_writers",
        "paid_count", "confirmed_count",
        "held_count", "pending_count",
        "created_at",
    )
    list_filter = (
        "status",
        "payment_window__status",
        "payment_window__website",
    )
    search_fields   = ("payment_window__title",)
    readonly_fields = (
        "payment_window", "total_amount", "total_writers",
        "created_by", "paid_at", "created_at", "updated_at",
    )
    list_select_related = ("payment_window",)
    date_hierarchy      = "created_at"
    inlines             = (PayoutRecordInline,)

    @admin.display(description="Status")
    def batch_status(self, obj):
        return badge(obj.status)

    @admin.display(description="Paid")
    def paid_count(self, obj):
        return obj.records.filter(status=PayoutRecordStatus.PAID).count()

    @admin.display(description="Confirmed")
    def confirmed_count(self, obj):
        return obj.records.filter(status=PayoutRecordStatus.CONFIRMED).count()

    @admin.display(description="Held")
    def held_count(self, obj):
        count = obj.records.filter(status=PayoutRecordStatus.HELD).count()
        if count:
            return format_html(
                '<span style="color:#B84232;font-weight:500">{}</span>', count,
            )
        return count

    @admin.display(description="Pending")
    def pending_count(self, obj):
        return obj.records.filter(status=PayoutRecordStatus.PENDING).count()


# ===========================================================================
# PAYOUT RECORD
# ===========================================================================

@admin.register(PayoutRecord)
class PayoutRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id", "writer", "batch",
        "total_amount", "record_status",
        "confirmed_at", "paid_at",
    )
    list_filter = (
        "status",
        "batch__payment_window__website",
    )
    search_fields = (
        "writer__account_profile__user__email",
        "writer__account_profile__user__first_name",
        "external_reference",
    )
    readonly_fields = (
        "website", "batch", "writer",
        "total_amount", "settlement_period",
        "confirmed_at", "confirmed_by",
        "paid_at", "paid_by",
    )
    list_select_related = ("writer__account_profile__user", "batch")
    autocomplete_fields = ("writer",)
    inlines             = (PayoutClearanceInline,)
    actions             = ("action_confirm", "action_mark_paid", "action_hold", "action_release")

    fieldsets = (
        ("Record", {
            "fields": ("website", "batch", "writer", "settlement_period"),
        }),
        ("Financials", {
            "fields": ("total_amount", "status", "hold_reason"),
        }),
        ("Confirmation", {
            "fields": ("confirmed_at", "confirmed_by"),
        }),
        ("Payment", {
            "fields": ("paid_at", "paid_by", "external_reference", "notes"),
        }),
    )

    @admin.display(description="Status")
    def record_status(self, obj):
        return badge(obj.status)

    @admin.action(description="Confirm selected records")
    def action_confirm(self, request, queryset):
        for record in queryset.filter(status=PayoutRecordStatus.PENDING):
            try:
                PayoutEngineService.confirm_record(record, confirmed_by=request.user)
            except Exception as exc:
                self.message_user(request, f"Record {record.pk}: {exc}", level="error")

    @admin.action(description="Mark selected records as paid")
    def action_mark_paid(self, request, queryset):
        for record in queryset.filter(status=PayoutRecordStatus.CONFIRMED):
            try:
                PayoutEngineService.mark_record_paid(record, paid_by=request.user)
            except Exception as exc:
                self.message_user(request, f"Record {record.pk}: {exc}", level="error")

    @admin.action(description="Hold selected records")
    def action_hold(self, request, queryset):
        for record in queryset.exclude(status=PayoutRecordStatus.PAID):
            try:
                PayoutEngineService.hold_record(
                    record,
                    reason="Held via admin bulk action.",
                    held_by=request.user,
                )
            except Exception as exc:
                self.message_user(request, f"Record {record.pk}: {exc}", level="error")

    @admin.action(description="Release held records back to PENDING")
    def action_release(self, request, queryset):
        for record in queryset.filter(status=PayoutRecordStatus.HELD):
            try:
                PayoutEngineService.release_held_record(record, released_by=request.user)
            except Exception as exc:
                self.message_user(request, f"Record {record.pk}: {exc}", level="error")


# ===========================================================================
# WRITER PAYOUT PREFERENCE
# ===========================================================================

@admin.register(WriterPayoutPreference)
class WriterPayoutPreferenceAdmin(admin.ModelAdmin):
    list_display    = ("id", "writer", "website", "cycle_type", "locked", "updated_at")
    list_filter     = ("cycle_type", "locked", "website")
    search_fields   = ("writer__account_profile__user__email",)
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("writer",)


# ===========================================================================
# CYCLE CHANGE REQUEST
# ===========================================================================

@admin.register(PaymentWindowChangeRequest)
class PaymentWindowChangeRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id", "writer",
        "from_window", "requested_window",
        "request_status", "reviewed_by",
        "reviewed_at", "created_at",
    )
    list_filter   = ("status", "website")
    search_fields = ("writer__account_profile__user__email",)
    readonly_fields = (
        "writer", "website",
        "from_window", "requested_window",
        "reason", "status",
        "reviewed_by", "reviewed_at",
        "rejection_reason", "effective_from_window",
        "created_at", "updated_at",
    )
    ordering            = ("-created_at",)
    autocomplete_fields = ("writer",)

    @admin.display(description="Status")
    def request_status(self, obj):
        return badge(obj.status)


# ===========================================================================
# COMPENSATION ADJUSTMENT
# ===========================================================================

@admin.register(CompensationAdjustment)
class CompensationAdjustmentAdmin(admin.ModelAdmin):
    list_display = (
        "id", "writer", "adjustment_type",
        "direction", "amount_display",
        "is_applied", "applied_at",
        "created_by", "created_at",
    )
    list_filter   = ("adjustment_type", "direction", "is_applied", "website")
    search_fields = ("writer__account_profile__user__email", "reason")
    readonly_fields = (
        "website", "writer",
        "related_financial_event",
        "created_by", "created_at",
    )
    autocomplete_fields = ("writer",)
    date_hierarchy      = "created_at"

    @admin.display(description="Amount")
    def amount_display(self, obj):
        return format_html(amount_html(
            obj.amount,
            positive_is_green=(obj.direction == "CREDIT"),
        ))


# ===========================================================================
# ADVANCE PAYMENT REQUEST
# ===========================================================================

@admin.register(AdvancePaymentRequest)
class AdvancePaymentRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id", "writer", "website",
        "requested_amount", "approved_amount",
        "recovered_amount", "outstanding",
        "advance_status", "reviewed_at", "created_at",
    )
    list_filter   = ("status", "website")
    search_fields = ("writer__account_profile__user__email", "reason")
    readonly_fields = (
        "writer", "website", "payment_window",
        "requested_by", "reviewed_by", "reviewed_at",
        "created_at", "updated_at",
    )
    autocomplete_fields = ("writer",)
    date_hierarchy      = "created_at"
    inlines             = (AdvanceRecoveryInline,)

    @admin.display(description="Status")
    def advance_status(self, obj):
        return badge(obj.status)

    @admin.display(description="Outstanding")
    def outstanding(self, obj):
        return format_html(amount_html(obj.outstanding_balance, positive_is_green=False))


@admin.register(AdvanceRecovery)
class AdvanceRecoveryAdmin(admin.ModelAdmin):
    list_display  = ("id", "advance_request", "amount", "settlement_period", "recovered_at")
    list_filter   = ("advance_request__website",)
    search_fields = ("advance_request__writer__account_profile__user__email",)
    readonly_fields = ("advance_request", "recovered_at")


# ===========================================================================
# DEFERRED SETTLEMENT ITEM
# ===========================================================================

@admin.register(DeferredSettlementItem)
class DeferredSettlementItemAdmin(admin.ModelAdmin):
    list_display = (
        "id", "financial_event",
        "from_payment_window", "to_payment_window",
        "reason", "deferred_by", "created_at",
    )
    list_filter   = ("reason", "from_payment_window__website")
    search_fields = ("financial_event__writer__account_profile__user__email",)
    readonly_fields = (
        "financial_event",
        "from_payment_window",
        "to_payment_window",
        "deferred_by",
        "created_at",
    )
    date_hierarchy = "created_at"


# ===========================================================================
# CORRECTION EVENT
# ===========================================================================

@admin.register(CorrectionEvent)
class CorrectionEventAdmin(admin.ModelAdmin):
    list_display = (
        "id", "writer", "correction_type",
        "expected", "actual",
        "difference", "correction_status",
        "resolved_at", "created_at",
    )
    list_filter   = ("correction_type", "status", "website")
    search_fields = ("writer__account_profile__user__email", "reason")
    readonly_fields = (
        "website", "writer",
        "expected", "actual",
        "difference", "delta_amount",
        "created_at",
    )
    date_hierarchy = "created_at"

    @admin.display(description="Status")
    def correction_status(self, obj):
        return badge(obj.status)


# ===========================================================================
# WRITER BALANCE SNAPSHOT
# ===========================================================================

@admin.register(WriterBalanceSnapshot)
class WriterBalanceSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "id", "writer", "payment_window",
        "wallet_balance", "gross_earnings",
        "net_payable", "total_deductions",
        "total_advances", "captured_at",
    )
    list_filter   = ("website", "payment_window")
    search_fields = ("writer__account_profile__user__email",)
    readonly_fields = (
        "website", "writer", "payment_window",
        "wallet_balance", "gross_earnings",
        "net_payable", "total_deductions",
        "total_advances", "total_pending",
        "captured_at",
    )
    ordering       = ("-captured_at",)
    date_hierarchy = "captured_at"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ===========================================================================
# EXPOSURE LEDGER
# ===========================================================================

@admin.register(ExposureLedger)
class ExposureLedgerAdmin(admin.ModelAdmin):
    list_display = (
        "id", "writer", "website",
        "total_earned", "total_bonuses",
        "total_deductions", "total_advance_taken",
        "total_settled", "total_paid",
        "recoverable_balance", "risk_cap_percentage",
        "last_updated",
    )
    list_filter   = ("website",)
    search_fields = ("writer__account_profile__user__email",)
    readonly_fields = (
        "website", "writer",
        "total_earned", "total_bonuses",
        "total_deductions", "total_settled",
        "total_paid", "total_advance_taken",
        "recoverable_balance", "last_updated",
    )
    ordering = ("-last_updated",)

    fieldsets = (
        ("Writer", {
            "fields": ("website", "writer"),
        }),
        ("Earnings", {
            "fields": ("total_earned", "total_bonuses"),
        }),
        ("Deductions", {
            "fields": ("total_deductions", "total_advance_taken"),
        }),
        ("Settlement", {
            "fields": ("total_settled", "total_paid"),
        }),
        ("Risk", {
            "fields": ("risk_cap_percentage", "recoverable_balance"),
        }),
        ("Audit", {
            "fields": ("last_updated",),
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ===========================================================================
# PAYOUT CLEARANCE
# ===========================================================================

@admin.register(PayoutClearance)
class PayoutClearanceAdmin(admin.ModelAdmin):
    list_display = (
        "id", "payout_record", "amount_sent",
        "method", "external_reference",
        "clearance_status", "processed_by", "processed_at",
    )
    list_filter   = ("status", "method", "website")
    search_fields = ("external_reference", "payout_record__writer__account_profile__user__email")
    readonly_fields = (
        "website", "payout_record",
        "processed_by", "processed_at",
        "created_at",
    )
    date_hierarchy = "created_at"

    @admin.display(description="Status")
    def clearance_status(self, obj):
        return badge(obj.status)


# ===========================================================================
# PAYOUT RECONCILIATION REPORT
# ===========================================================================

@admin.register(PayoutReconciliationReport)
class PayoutReconciliationReportAdmin(admin.ModelAdmin):
    list_display = (
        "id", "website", "payout_batch",
        "total_ledger_amount", "total_payout_amount",
        "total_cleared_amount", "mismatch_display",
        "report_status", "created_at",
    )
    list_filter   = ("status", "website")
    search_fields = ("payout_batch__payment_window__title",)
    readonly_fields = (
        "website", "payout_batch",
        "total_ledger_amount", "total_payout_amount",
        "total_cleared_amount", "mismatch_amount",
        "status", "created_at",
    )
    ordering       = ("-created_at",)
    date_hierarchy = "created_at"

    @admin.display(description="Mismatch")
    def mismatch_display(self, obj):
        if obj.mismatch_amount == 0:
            return format_html(
                '<span style="color:green;font-weight:500">✓ Balanced</span>'
            )
        return format_html(
            '<span style="color:red;font-weight:500">{}</span>',
            obj.mismatch_amount,
        )

    @admin.display(description="Status")
    def report_status(self, obj):
        return badge(obj.status)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ===========================================================================
# REVERSAL CHAIN
# ===========================================================================

@admin.register(ReversalChain)
class ReversalChainAdmin(admin.ModelAdmin):
    list_display = (
        "id", "website",
        "original_event", "reversal_event",
        "reason_short", "created_at",
    )
    list_filter   = ("website",)
    search_fields = (
        "original_event__writer__account_profile__user__email",
        "reason",
    )
    readonly_fields = (
        "website", "original_event",
        "reversal_event", "reason",
        "created_at",
    )
    ordering       = ("-created_at",)
    date_hierarchy = "created_at"

    @admin.display(description="Reason")
    def reason_short(self, obj):
        return obj.reason[:60] + "…" if len(obj.reason) > 60 else obj.reason

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ===========================================================================
# IDEMPOTENCY RECORD
# ===========================================================================

@admin.register(IdempotencyRecord)
class IdempotencyRecordAdmin(admin.ModelAdmin):
    list_display  = ("id", "scope", "key", "created_at")
    list_filter   = ("scope",)
    search_fields = ("key", "scope")
    readonly_fields = ("key", "scope", "request_hash", "response", "created_at")
    ordering       = ("-created_at",)
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ===========================================================================
# OUTBOX EVENT
# ===========================================================================

@admin.register(OutboxEvent)
class OutboxEventAdmin(admin.ModelAdmin):
    list_display = (
        "id", "event_type",
        "outbox_status", "retry_count",
        "processed", "processed_at",
        "created_at",
    )
    list_filter   = ("status", "event_type", "processed")
    search_fields = ("event_type", "payload_hash")
    readonly_fields = (
        "event_type", "payload", "payload_hash",
        "status", "processed", "processing",
        "retry_count", "last_error",
        "processed_at", "created_at",
    )
    ordering       = ("-created_at",)
    date_hierarchy = "created_at"
    actions        = ("action_retry",)

    @admin.display(description="Status")
    def outbox_status(self, obj):
        return badge(obj.status)

    @admin.action(description="Reset selected DEAD events for retry")
    def action_retry(self, request, queryset):
        updated = queryset.filter(
            status=OutboxEvent.Status.DEAD,
        ).update(
            status=OutboxEvent.Status.PENDING,
            retry_count=0,
            last_error=None,
        )
        self.message_user(request, f"{updated} event(s) reset for retry.")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False