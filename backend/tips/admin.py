from __future__ import annotations

from django.contrib import admin

from tips.models.tip import Tip
from tips.models.tip_analytics_daily import TipAnalyticsDaily
from tips.models.tip_attribution import TipAttribution
from tips.models.tip_idempotency import TipIdempotencyKey
from tips.models.tip_outbox_event import TipOutboxEvent
from tips.models.tip_policy import TipPolicy
from tips.models.tip_policy_snapshot import TipPolicySnapshot
from tips.models.tip_settlement_snapshot import TipSettlementSnapshot


@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "status", "gross_amount_cents", "created_at")
    list_filter = ("status", "currency", "source_type", "created_at")
    search_fields = ("id", "sender__email", "receiver__email")


@admin.register(TipAttribution)
class TipAttributionAdmin(admin.ModelAdmin):
    list_display = ("id", "tip", "context_type", "created_at")
    list_filter = ("context_type", "created_at")
    search_fields = ("tip__id", "reason")


@admin.register(TipPolicy)
class TipPolicyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "writer_percentage", "platform_percentage", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "slug")


@admin.register(TipPolicySnapshot)
class TipPolicySnapshotAdmin(admin.ModelAdmin):
    list_display = ("id", "tip", "writer_percentage", "platform_percentage")
    search_fields = ("tip__id",)


@admin.register(TipSettlementSnapshot)
class TipSettlementSnapshotAdmin(admin.ModelAdmin):
    list_display = ("id", "tip", "gross_amount", "writer_tip_share", "platform_tip_share", "settled_at")
    search_fields = ("tip__id",)


@admin.register(TipAnalyticsDaily)
class TipAnalyticsDailyAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "total_tips", "total_volume_cents", "created_at")
    list_filter = ("date",)


@admin.register(TipIdempotencyKey)
class TipIdempotencyKeyAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "tip", "created_at")
    search_fields = ("key", "tip__id")


@admin.register(TipOutboxEvent)
class TipOutboxEventAdmin(admin.ModelAdmin):
    list_display = ("id", "tip", "event_type", "status", "processed", "failed", "created_at")
    list_filter = ("event_type", "status", "processed", "failed")
    search_fields = ("tip__id", "deduplication_key")
