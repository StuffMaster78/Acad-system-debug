# tips/admin.py

from __future__ import annotations

from django.contrib import admin
from django.http import HttpRequest

from tips.enums.tip_status import TipStatus

from tips.models.tip import Tip
from tips.models.tip_attribution import TipAttribution
from tips.models.tip_policy import TipPolicy
from tips.models.tip_policy_snapshot import TipPolicySnapshot
from tips.models.tip_settlement_snapshot import (
    TipSettlementSnapshot,
)
from tips.models.tip_analytics_daily import (
    TipAnalyticsDaily,
)
from tips.models.tip_idempotency import (
    TipIdempotencyKey,
)
from tips.models.tip_outbox_event import (
    TipOutboxEvent,
)


# ============================================================ #
# TIP
# ============================================================ #

@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "sender",
        "receiver",
        "gross_amount_cents",
        "writer_share_cents",
        "platform_fee_cents",
        "currency",
        "status",
        "source_type",
        "is_settled",
        "created_at",
    ]

    list_filter = [
        "status",
        "currency",
        "source_type",
        "is_settled",
        "created_at",
        "settled_at",
    ]

    search_fields = [
        "id",
        "sender__email",
        "receiver__email",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "settled_at",
        "is_settled",
    ]

    autocomplete_fields = [
        "sender",
        "receiver",
        "payment_intent",
        "active_policy",
    ]

    ordering = [
        "-created_at",
    ]

    list_select_related = [
        "sender",
        "receiver",
        "payment_intent",
        "active_policy",
    ]

    date_hierarchy = "created_at"

    actions = [
        "mark_as_failed",
    ]

    fieldsets = (
        (
            "Core",
            {
                "fields": (
                    "sender",
                    "receiver",
                    "status",
                    "source_type",
                    "currency",
                )
            },
        ),
        (
            "Financials",
            {
                "fields": (
                    "gross_amount_cents",
                    "writer_share_cents",
                    "platform_fee_cents",
                )
            },
        ),
        (
            "Settlement",
            {
                "fields": (
                    "is_settled",
                    "settled_at",
                )
            },
        ),
        (
            "Relationships",
            {
                "fields": (
                    "payment_intent",
                    "active_policy",
                )
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "client_note",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.action(description="Mark selected tips as failed")
    def mark_as_failed(
        self,
        request: HttpRequest,
        queryset,
    ):
        queryset.update(
            status=TipStatus.FAILED,
        )

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        """
        Financial records should never disappear.
        """
        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        """
        Settled financial records become immutable.
        """

        if obj and obj.is_settled:
            return request.user.is_superuser

        return super().has_change_permission(
            request,
            obj,
        )


# ============================================================ #
# TIP ATTRIBUTION
# ============================================================ #

@admin.register(TipAttribution)
class TipAttributionAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "tip",
        "context_type",
        "order",
        "special_order",
        "class_purchase",
        "created_at",
    ]

    list_filter = [
        "context_type",
        "created_at",
    ]

    search_fields = [
        "tip__id",
        "reason",
    ]

    readonly_fields = [
        "created_at",
    ]

    autocomplete_fields = [
        "tip",
        "order",
        "special_order",
        "class_purchase",
    ]

    ordering = [
        "-created_at",
    ]

    date_hierarchy = "created_at"

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False


# ============================================================ #
# TIP POLICY
# ============================================================ #

@admin.register(TipPolicy)
class TipPolicyAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "name",
        "minimum_tip_amount_cents",
        "maximum_tip_amount_cents",
        "platform_fee_percentage",
        "is_active",
        "created_at",
    ]

    list_filter = [
        "is_active",
        "created_at",
    ]

    search_fields = [
        "name",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
    ]

    ordering = [
        "-created_at",
    ]

    date_hierarchy = "created_at"

    actions = [
        "activate_policy",
    ]

    @admin.action(description="Activate selected policy")
    def activate_policy(
        self,
        request,
        queryset,
    ):
        TipPolicy.objects.update(
            is_active=False,
        )

        queryset.update(
            is_active=True,
        )


# ============================================================ #
# TIP POLICY SNAPSHOT
# ============================================================ #

@admin.register(TipPolicySnapshot)
class TipPolicySnapshotAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "tip",
        "policy_name",
        "platform_fee_percentage",
        "created_at",
    ]

    list_filter = [
        "created_at",
    ]

    search_fields = [
        "tip__id",
        "policy_name",
    ]

    readonly_fields = [
        "created_at",
    ]

    autocomplete_fields = [
        "tip",
    ]

    ordering = [
        "-created_at",
    ]

    date_hierarchy = "created_at"

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False


# ============================================================ #
# TIP SETTLEMENT SNAPSHOT
# ============================================================ #

@admin.register(TipSettlementSnapshot)
class TipSettlementSnapshotAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "tip",
        "gross_amount_cents",
        "writer_share_cents",
        "platform_fee_cents",
        "settlement_status",
        "settled_at",
    ]

    list_filter = [
        "settlement_status",
        "settled_at",
    ]

    search_fields = [
        "tip__id",
    ]

    readonly_fields = [
        "created_at",
        "settled_at",
    ]

    autocomplete_fields = [
        "tip",
    ]

    ordering = [
        "-created_at",
    ]

    date_hierarchy = "settled_at"

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False


# ============================================================ #
# DAILY ANALYTICS
# ============================================================ #

@admin.register(TipAnalyticsDaily)
class TipAnalyticsDailyAdmin(admin.ModelAdmin):

    list_display = [
        "date",
        "tip_count",
        "gross_volume_cents",
        "writer_total_cents",
        "platform_total_cents",
        "success_rate",
    ]

    list_filter = [
        "date",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
    ]

    ordering = [
        "-date",
    ]

    date_hierarchy = "date"

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False


# ============================================================ #
# IDEMPOTENCY
# ============================================================ #

@admin.register(TipIdempotencyKey)
class TipIdempotencyKeyAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "sender",
        "key",
        "tip",
        "created_at",
    ]

    search_fields = [
        "key",
        "sender__email",
    ]

    readonly_fields = [
        "created_at",
    ]

    autocomplete_fields = [
        "sender",
        "tip",
    ]

    ordering = [
        "-created_at",
    ]

    date_hierarchy = "created_at"

    def has_add_permission(
        self,
        request,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False


# ============================================================ #
# OUTBOX EVENTS
# ============================================================ #

@admin.register(TipOutboxEvent)
class TipOutboxEventAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "tip",
        "event_type",
        "processed",
        "failed",
        "created_at",
        "processed_at",
    ]

    list_filter = [
        "event_type",
        "processed",
        "failed",
        "created_at",
    ]

    search_fields = [
        "tip__id",
        "event_type",
    ]

    readonly_fields = [
        "created_at",
        "processed_at",
        "failure_reason",
    ]

    autocomplete_fields = [
        "tip",
    ]

    ordering = [
        "-created_at",
    ]

    date_hierarchy = "created_at"

    actions = [
        "reset_failed_events",
    ]

    @admin.action(description="Reset failed outbox events")
    def reset_failed_events(
        self,
        request,
        queryset,
    ):
        queryset.update(
            failed=False,
            processed=False,
            failure_reason="",
        )

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False