from __future__ import annotations

from django.contrib import admin

from activity.models import ActivityEvent
from activity.models import ActivityFeedState


@admin.register(ActivityEvent)
class ActivityEventAdmin(admin.ModelAdmin):
    """
    Admin configuration for activity events.
    """

    list_display = (
        "verb",
        "website",
        "actor_type",
        "severity",
        "occurred_at",
    )
    list_filter = (
        "verb",
        "actor_type",
        "severity",
        "website",
    )
    search_fields = (
        "title",
        "summary",
        "target_object_id",
        "actor_object_id",
        "request_id",
    )
    readonly_fields = (
        "id",
        "website",
        "verb",
        "actor_type",
        "actor_content_type",
        "actor_object_id",
        "target_content_type",
        "target_object_id",
        "subject_content_type",
        "subject_object_id",
        "severity",
        "audiences",
        "title",
        "summary",
        "metadata",
        "request_id",
        "ip_address",
        "user_agent",
        "occurred_at",
        "created_at",
    )
    ordering = (
        "-occurred_at",
    )

    def has_add_permission(self, request):
        """
        Prevent manual activity creation from admin.
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Allow viewing but prevent mutation.
        """
        return bool(request.user and request.user.is_staff)

    def has_delete_permission(self, request, obj=None):
        """
        Prevent activity deletion from admin.
        """
        return False


@admin.register(ActivityFeedState)
class ActivityFeedStateAdmin(admin.ModelAdmin):
    """
    Admin configuration for per user feed state.
    """

    list_display = (
        "event",
        "user",
        "is_read",
        "is_dismissed",
        "is_pinned",
        "created_at",
    )
    list_filter = (
        "is_read",
        "is_dismissed",
        "is_pinned",
    )
    search_fields = (
        "user__username",
        "user__email",
    )
    readonly_fields = (
        "id",
        "event",
        "user",
        "created_at",
    )