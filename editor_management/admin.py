from django.contrib import admin
from .models import (
    EditorProfile,
    EditorTaskAssignment,
    EditorActionLog,
    EditorPerformance,
    EditorNotification,
)

@admin.register(EditorProfile)
class EditorProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "registration_id", "email", "is_active", "last_logged_in")
    search_fields = ("name", "registration_id", "email")
    list_filter = ("is_active",)
    ordering = ("name",)


@admin.register(EditorTaskAssignment)
class EditorTaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ("order", "assigned_editor", "review_status", "reviewed_at")
    list_filter = ("review_status", "reviewed_at")
    search_fields = ("order__id", "assigned_editor__name")


@admin.register(EditorActionLog)
class EditorActionLogAdmin(admin.ModelAdmin):
    list_display = ("editor", "action", "related_order", "timestamp")
    search_fields = ("editor__name", "action", "related_order__id")
    ordering = ("-timestamp",)


@admin.register(EditorPerformance)
class EditorPerformanceAdmin(admin.ModelAdmin):
    list_display = ("editor", "average_review_time", "total_orders_reviewed", "late_reviews")
    search_fields = ("editor__name",)
    ordering = ("-total_orders_reviewed",)


@admin.register(EditorNotification)
class EditorNotificationAdmin(admin.ModelAdmin):
    list_display = ("editor", "message", "created_at", "is_read")
    list_filter = ("is_read",)
    search_fields = ("editor__name", "message")