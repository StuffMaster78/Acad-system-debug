from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html

from writer_compensation.enums.compensation_enums import (
    PayoutItemStatus,
    WindowStatus,
)
from writer_compensation.models.compensation_event import (
    CompensationEvent,
)
from writer_compensation.models.cycle_change_request import (
    PaymentWindowChangeRequest,
)
from writer_compensation.models.payment_window import (
    PaymentWindow,
)
from writer_compensation.models.payout_batch import (
    PayoutBatch,
)
from writer_compensation.models.payout_record import (
    PayoutRecord,
)
from writer_compensation.models.writer_payout_preference import (
    WriterPayoutPreference,
)
from writer_compensation.services.payout_engine_service import (
    PayoutEngineService,
)
from writer_compensation.services.window_service import (
    WindowService,
)


# ===========================================================================
# HELPERS
# ===========================================================================

def render_status_badge(label: str, colours: dict[str, tuple[str, str]]) -> str:
    bg, fg = colours.get(label, ("777777", "white"))

    return format_html(
        (
            '<span style="background:{};color:{};'
            'padding:2px 8px;border-radius:4px;'
            'font-size:11px;font-weight:500">'
            "{}"
            "</span>"
        ),
        f"#{bg}",
        fg,
        label,
    )


# ===========================================================================
# INLINES
# ===========================================================================

class CompensationEventInline(admin.TabularInline):
    model = CompensationEvent
    extra = 0
    can_delete = False
    show_change_link = True

    fields = (
        "event_type",
        "amount",
        "status",
        "source_type",
        "source_id",
        "created_at",
    )

    readonly_fields = fields


class PayoutRecordInline(admin.TabularInline):
    model = PayoutRecord
    extra = 0
    can_delete = False
    show_change_link = True

    fields = (
        "writer",
        "total_amount",
        "status",
        "confirmed_at",
        "paid_at",
    )

    readonly_fields = fields


# ===========================================================================
# PAYMENT WINDOW ADMIN
# ===========================================================================

@admin.register(PaymentWindow)
class PaymentWindowAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "window_type",
        "start_date",
        "end_date",
        "status_badge",
        "event_count",
        "created_at",
    )

    list_filter = (
        "status",
        "cycle_type",
        "website",
    )

    search_fields = ("website__name",)

    readonly_fields = (
        "status",
        "closed_at",
        "processing_at",
        "done_at",
        "created_at",
        "updated_at",
    )

    ordering = ("-start_date",)

    list_select_related = ("website",)

    date_hierarchy = "created_at"

    inlines = (
        CompensationEventInline,
        PayoutRecordInline,
    )

    actions = (
        "action_close",
        "action_start_processing",
        "action_mark_done",
    )

    @admin.display(description="Status")
    def status_badge(self, obj):
        return render_status_badge(
            obj.get_status_display(),
            {
                WindowStatus.OPEN: ("1B6AAA", "white"),
                WindowStatus.CLOSED: ("8B5E0A", "white"),
                WindowStatus.PROCESSING: ("0E6B74", "white"),
                WindowStatus.DONE: ("1A5C2A", "white"),
            },
        )

    @admin.display(description="Events")
    def event_count(self, obj):
        return CompensationEvent.objects.filter(window=obj).count()

    @admin.action(description="Close selected windows")
    def action_close(self, request, queryset):
        for window in queryset.filter(status=WindowStatus.OPEN):
            try:
                WindowService.close_window(
                    window,
                    closed_by=request.user,
                )

                self.message_user(
                    request,
                    f"Window {window.pk} closed.",
                )

            except Exception as exc:
                self.message_user(
                    request,
                    f"Window {window.pk}: {exc}",
                    level="error",
                )

    @admin.action(description="Start processing selected windows")
    def action_start_processing(self, request, queryset):
        for window in queryset.filter(status=WindowStatus.CLOSED):
            try:
                WindowService.start_processing(window)

                self.message_user(
                    request,
                    f"Window {window.pk} → PROCESSING.",
                )

            except Exception as exc:
                self.message_user(
                    request,
                    f"Window {window.pk}: {exc}",
                    level="error",
                )

    @admin.action(description="Mark selected windows done")
    def action_mark_done(self, request, queryset):
        for window in queryset.filter(status=WindowStatus.PROCESSING):
            try:
                WindowService.mark_done(window)

                self.message_user(
                    request,
                    f"Window {window.pk} → DONE.",
                )

            except Exception as exc:
                self.message_user(
                    request,
                    f"Window {window.pk}: {exc}",
                    level="error",
                )


# ===========================================================================
# COMPENSATION EVENT ADMIN
# ===========================================================================

@admin.register(CompensationEvent)
class CompensationEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "writer",
        "event_type",
        "amount_display",
        "status",
        "source_type",
        "source_id",
        "window",
        "created_at",
    )

    list_filter = (
        "event_type",
        "status",
        "window__website",
    )

    search_fields = (
        "writer__user__email",
        "writer__user__first_name",
        "idempotency_key",
        "source_id",
    )

    readonly_fields = (
        "website",
        "writer",
        "window",
        "related_window",
        "event_type",
        "amount",
        "status",
        "source_type",
        "source_id",
        "idempotency_key",
        "created_by",
        "created_at",
    )

    ordering = ("-created_at",)

    list_select_related = (
        "writer__user",
        "window",
    )

    date_hierarchy = "created_at"

    @admin.display(description="Amount")
    def amount_display(self, obj):
        colour = "green" if obj.amount > 0 else "red"

        return format_html(
            '<span style="color:{};font-weight:500">{}</span>',
            colour,
            obj.amount,
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ===========================================================================
# PAYOUT BATCH ADMIN
# ===========================================================================

@admin.register(PayoutBatch)
class PayoutBatchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "window",
        "total_amount",
        "paid_count",
        "held_count",
        "pending_count",
        "created_at",
    )

    list_filter = (
        "window__status",
        "window__website",
    )

    readonly_fields = (
        "window",
        "total_amount",
        "created_by",
        "paid_at",
        "created_at",
        "updated_at",
    )

    list_select_related = ("window",)

    date_hierarchy = "created_at"

    inlines = (PayoutRecordInline,)

    @admin.display(description="Paid")
    def paid_count(self, obj):
        return obj.items.filter(
            status=PayoutItemStatus.PAID,
        ).count()

    @admin.display(description="Held")
    def held_count(self, obj):
        count = obj.items.filter(
            status=PayoutItemStatus.HELD,
        ).count()

        if count:
            return format_html(
                '<span style="color:red;font-weight:500">{}</span>',
                count,
            )

        return count

    @admin.display(description="Pending")
    def pending_count(self, obj):
        return obj.items.filter(
            status=PayoutItemStatus.PENDING,
        ).count()


# ===========================================================================
# PAYOUT RECORD ADMIN
# ===========================================================================

@admin.register(PayoutRecord)
class PayoutRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "writer",
        "batch",
        "total_amount",
        "status_badge",
        "confirmed_at",
        "paid_at",
    )

    list_filter = (
        "status",
        "batch__window__website",
    )

    search_fields = (
        "writer__user__email",
        "writer__user__first_name",
    )

    readonly_fields = (
        "batch",
        "writer",
        "total_amount",
        "confirmed_at",
        "confirmed_by",
        "paid_at",
        "paid_by",
    )

    list_select_related = (
        "writer__user",
        "batch",
    )

    autocomplete_fields = ("writer",)

    actions = (
        "action_confirm",
        "action_mark_paid",
        "action_hold",
    )

    @admin.display(description="Status")
    def status_badge(self, obj):
        return render_status_badge(
            obj.get_status_display(),
            {
                PayoutItemStatus.PENDING: ("8B5E0A", "white"),
                PayoutItemStatus.CONFIRMED: ("1B6AAA", "white"),
                PayoutItemStatus.PAID: ("1A5C2A", "white"),
                PayoutItemStatus.HELD: ("B84232", "white"),
            },
        )

    @admin.action(description="Confirm selected payout items")
    def action_confirm(self, request, queryset):
        for record in queryset.filter(
            status=PayoutItemStatus.PENDING,
        ):
            try:
                PayoutEngineService.confirm_record(
                    record,
                    confirmed_by=request.user,
                )

            except Exception as exc:
                self.message_user(
                    request,
                    f"Record {record.pk}: {exc}",
                    level="error",
                )

    @admin.action(description="Mark selected items as paid")
    def action_mark_paid(self, request, queryset):
        for record in queryset.filter(
            status=PayoutItemStatus.CONFIRMED,
        ):
            try:
                PayoutEngineService.mark_record_paid(
                    record,
                    paid_by=request.user,
                )

            except Exception as exc:
                self.message_user(
                    request,
                    f"Record {record.pk}: {exc}",
                    level="error",
                )

    @admin.action(description="Hold selected payout items")
    def action_hold(self, request, queryset):
        for record in queryset.exclude(
            status=PayoutItemStatus.PAID,
        ):
            try:
                PayoutEngineService.hold_record(
                    record,
                    reason="Held via admin bulk action.",
                    held_by=request.user,
                )

            except Exception as exc:
                self.message_user(
                    request,
                    f"Record {record.pk}: {exc}",
                    level="error",
                )


# ===========================================================================
# WRITER PAYOUT PREFERENCE ADMIN
# ===========================================================================

@admin.register(WriterPayoutPreference)
class WriterPayoutPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "writer",
        "website",
        "window_type",
        "locked",
        "updated_at",
    )

    list_filter = (
        "window_type",
        "locked",
        "website",
    )

    search_fields = ("writer__user__email",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = ("writer",)


# ===========================================================================
# PAYMENT WINDOW CHANGE REQUEST ADMIN
# ===========================================================================

@admin.register(PaymentWindowChangeRequest)
class PaymentWindowChangeRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "writer",
        "from_window",
        "requested_window",
        "status",
        "reviewed_by",
        "reviewed_at",
        "created_at",
    )

    list_filter = (
        "status",
        "website",
    )

    search_fields = ("writer__user__email",)

    readonly_fields = (
        "writer",
        "website",
        "from_window",
        "requested_window",
        "reason",
        "status",
        "reviewed_by",
        "reviewed_at",
        "rejection_reason",
        "effective_from_window",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    autocomplete_fields = ("writer",)