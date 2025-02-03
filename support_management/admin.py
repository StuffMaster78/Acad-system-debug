from django.contrib import admin
from .models import (
    SupportProfile, SupportNotification, SupportOrderManagement,
    SupportMessage, SupportMessageAccess, SupportGlobalAccess,
    SupportPermission, DisputeResolutionLog, SupportActionLog,
    EscalationLog, SupportAvailability, SupportActivityLog,
    PaymentIssueLog, SupportOrderFileManagement, WriterPerformanceLog,
    SupportWorkloadTracker, OrderDisputeSLA, FAQCategory, FAQManagement,
    SupportDashboard
)


@admin.register(SupportProfile)
class SupportProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone_number", "status", "last_logged_in")
    search_fields = ("name", "email", "registration_id")
    list_filter = ("status",)


@admin.register(SupportNotification)
class SupportNotificationAdmin(admin.ModelAdmin):
    list_display = ("support_staff", "message", "priority", "created_at", "is_read")
    search_fields = ("support_staff__name", "message")
    list_filter = ("priority", "is_read")


@admin.register(SupportOrderManagement)
class SupportOrderManagementAdmin(admin.ModelAdmin):
    list_display = ("support_staff", "order", "action", "timestamp", "admin_reviewed")
    search_fields = ("support_staff__name", "order__id", "action")
    list_filter = ("admin_reviewed", "timestamp")


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "order", "message", "timestamp", "is_read")
    search_fields = ("sender__username", "recipient__username", "order__id")
    list_filter = ("is_read", "timestamp")


@admin.register(SupportMessageAccess)
class SupportMessageAccessAdmin(admin.ModelAdmin):
    list_display = ("support_staff", "can_view_order_messages", "can_moderate_messages")


@admin.register(SupportGlobalAccess)
class SupportGlobalAccessAdmin(admin.ModelAdmin):
    list_display = ("support_staff", "can_view_orders", "can_view_clients", "can_view_writers")


@admin.register(SupportPermission)
class SupportPermissionAdmin(admin.ModelAdmin):
    list_display = ("support_staff", "can_manage_tickets", "can_handle_disputes", "can_promote_writer")


@admin.register(DisputeResolutionLog)
class DisputeResolutionLogAdmin(admin.ModelAdmin):
    list_display = ("dispute", "resolved_by", "resolved_at")
    search_fields = ("resolved_by__name", "dispute__id")


@admin.register(SupportActionLog)
class SupportActionLogAdmin(admin.ModelAdmin):
    list_display = ("support_staff", "action", "timestamp")
    search_fields = ("support_staff__name", "action")


@admin.register(EscalationLog)
class EscalationLogAdmin(admin.ModelAdmin):
    list_display = ("escalated_by", "action_type", "target_user", "status", "timestamp")
    search_fields = ("escalated_by__name", "target_user__username", "action_type")
    list_filter = ("status", "timestamp")


@admin.register(SupportAvailability)
class SupportAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("support_staff", "status", "is_online", "last_checked_in")
    list_filter = ("status", "is_online")


@admin.register(SupportActivityLog)
class SupportActivityLogAdmin(admin.ModelAdmin):
    list_display = ("support_staff", "action_type", "timestamp")
    search_fields = ("support_staff__name", "action_type")


@admin.register(PaymentIssueLog)
class PaymentIssueLogAdmin(admin.ModelAdmin):
    list_display = ("order", "reported_by", "issue_type", "status", "reported_at")
    search_fields = ("order__id", "reported_by__name", "issue_type")
    list_filter = ("status", "reported_at")


@admin.register(SupportOrderFileManagement)
class SupportOrderFileManagementAdmin(admin.ModelAdmin):
    list_display = ("support_staff", "order", "file", "action", "timestamp")


@admin.register(WriterPerformanceLog)
class WriterPerformanceLogAdmin(admin.ModelAdmin):
    list_display = ("writer", "issue_type", "reported_by", "created_at", "resolved")
    list_filter = ("issue_type", "resolved")


@admin.register(SupportWorkloadTracker)
class SupportWorkloadTrackerAdmin(admin.ModelAdmin):
    list_display = ("support_staff", "tickets_handled", "disputes_handled", "orders_managed", "last_activity")


@admin.register(OrderDisputeSLA)
class OrderDisputeSLAAdmin(admin.ModelAdmin):
    list_display = ("sla_type", "order", "dispute", "assigned_to", "sla_breached")
    list_filter = ("sla_breached",)


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category_type", "created_at")


@admin.register(FAQManagement)
class FAQManagementAdmin(admin.ModelAdmin):
    list_display = ("category", "question", "created_by", "is_active", "created_at")
    search_fields = ("category__name", "question", "created_by__name")
    list_filter = ("is_active", "created_at")


@admin.register(SupportDashboard)
class SupportDashboardAdmin(admin.ModelAdmin):
    list_display = ("support_staff", "total_tickets_handled", "total_disputes_handled", "total_orders_managed")
    list_filter = ("last_updated",)
