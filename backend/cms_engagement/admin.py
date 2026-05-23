"""
Engagement Admin — read-only views for engagement data.
"""

from django.contrib import admin

from cms_engagement.models import (
    EngagementSummary,
    PageBookmark,
    PageReaction,
    PageShare,
    PageView,
)


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = [
        "content_object",
        "site",
        "time_on_page",
        "scroll_depth",
        "referrer_short",
        "created_at",
    ]
    list_filter = ["site", "created_at"]
    date_hierarchy = "created_at"
    readonly_fields = [
        "content_type",
        "object_id",
        "site",
        "session_id",
        "user",
        "ip_address",
        "referrer",
        "user_agent",
        "time_on_page",
        "scroll_depth",
        "created_at",
    ]

    def referrer_short(self, obj):
        return (obj.referrer or "—")[:60]

    referrer_short.short_description = "Referrer"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(PageReaction)
class PageReactionAdmin(admin.ModelAdmin):
    list_display = ["content_object", "reaction_type", "site", "created_at"]
    list_filter = ["reaction_type", "site"]
    readonly_fields = [
        "content_type", "object_id", "site", "user",
        "session_id", "reaction_type", "created_at",
    ]

    def has_add_permission(self, request):
        return False


@admin.register(PageShare)
class PageShareAdmin(admin.ModelAdmin):
    list_display = ["content_object", "platform", "site", "created_at"]
    list_filter = ["platform", "site"]

    def has_add_permission(self, request):
        return False


@admin.register(PageBookmark)
class PageBookmarkAdmin(admin.ModelAdmin):
    list_display = ["content_object", "user", "created_at"]

    def has_add_permission(self, request):
        return False


@admin.register(EngagementSummary)
class EngagementSummaryAdmin(admin.ModelAdmin):
    list_display = [
        "content_object",
        "site",
        "total_views",
        "unique_views",
        "avg_time_on_page",
        "thumbs_up_count",
        "useful_count",
        "total_shares",
        "engagement_score",
        "helpfulness_ratio",
        "last_computed",
    ]
    list_filter = ["site"]
    readonly_fields = [
        "content_type", "object_id", "site",
        "total_views", "unique_views", "avg_time_on_page",
        "avg_scroll_depth", "bounce_rate",
        "thumbs_up_count", "thumbs_down_count",
        "love_count", "useful_count", "total_shares",
        "engagement_score", "helpfulness_ratio",
        "last_computed",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False