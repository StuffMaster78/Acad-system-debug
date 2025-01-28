from django.contrib import admin
from .models import (
    SupportProfile,
    SupportActionLog,
    SupportActivityLog,
    DisputeResolutionLog,
    TicketAssignment,
    SupportAvailability,
    SupportPerformance,
    SupportNotification,
    EscalationLog,
)

@admin.register(SupportProfile)
class SupportProfileAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "registration_id",
        "email",
        "phone_number",
        "website",
        "orders_handled",
        "disputes_handled",
        "tickets_handled",
        "last_logged_in",
    )
    search_fields = ("name", "email", "registration_id")
    list_filter = ("website",)
    readonly_fields = ("orders_handled", "disputes_handled", "tickets_handled", "last_logged_in")

@admin.register(SupportActionLog)
class SupportActionLogAdmin(admin.ModelAdmin):
    list_display = ("support_staff", "action", "timestamp")
    search_fields = ("support_staff__name", "action")
    list_filter = ("action",)

@admin.register(SupportActivityLog)
class SupportActivityLogAdmin(admin.ModelAdmin):
    list_display = ("support_staff", "activity", "timestamp")
    search_fields = ("support_staff__name", "activity")
    list_filter = ("timestamp",)

@admin.register(DisputeResolutionLog)
class DisputeResolutionLogAdmin(admin.ModelAdmin):
    list_display = ("dispute", "resolved_by", "resolved_at")
    search_fields = ("resolved_by__name", "dispute__id")
    list_filter = ("resolved_at",)

@admin.register(TicketAssignment)
class TicketAssignmentAdmin(admin.ModelAdmin):
    list_display = ("ticket", "assigned_to", "assigned_at", "completed_at")
    search_fields = ("ticket__id", "assigned_to__name")
    list_filter = ("assigned_at", "completed_at")

@admin.register(SupportAvailability)
class SupportAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("support_staff", "start_time", "end_time", "is_recurring", "is_active")
    search_fields = ("support_staff__name",)
    list_filter = ("is_recurring", "is_active")

@admin.register(SupportPerformance)
class SupportPerformanceAdmin(admin.ModelAdmin):
    list_display = (
        "support_staff",
        "average_response_time",
        "average_resolution_time",
        "total_tickets_resolved",
        "total_disputes_resolved",
    )
    search_fields = ("support_staff__name",)
    list_filter = ("total_tickets_resolved", "total_disputes_resolved")

@admin.register(SupportNotification)
class SupportNotificationAdmin(admin.ModelAdmin):
    list_display = ("support_staff", "message", "is_read", "created_at")
    search_fields = ("support_staff__name", "message")
    list_filter = ("is_read", "created_at")

@admin.register(EscalationLog)
class EscalationLogAdmin(admin.ModelAdmin):
    list_display = ("escalated_by", "escalated_to", "timestamp", "reason")
    search_fields = ("escalated_by__name", "escalated_to__username", "reason")
    list_filter = ("timestamp",)