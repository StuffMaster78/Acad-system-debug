from django.contrib import admin
from .models import (
    OrderPayment, Refund, PaymentNotification, PaymentLog,
    PaymentDispute, SplitPayment, AdminLog,
    PaymentReminderSettings
)
# from discounts.models.discount import DiscountUsage
from django.utils import timezone

@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    """
    Admin panel customization for managing Order Payments.
    """
    list_display = (
        "transaction_id", "client", "payment_type",
        "discounted_amount", "payment_status", "payment_method", "date_processed"
    )
    list_filter = ("payment_status", "payment_type", "payment_method", "date_processed")
    search_fields = ("transaction_id", "client__username", "order__id")
    ordering = ("-date_processed",)
    readonly_fields = ("transaction_id", "client", "original_amount", "discounted_amount", "date_processed")
    actions = ["mark_as_completed", "mark_as_failed"]

    def mark_as_completed(self, request, queryset):
        queryset.update(status="completed")
        self.message_user(request, "Selected payments have been marked as completed.")

    def mark_as_failed(self, request, queryset):
        queryset.update(status="failed")
        self.message_user(request, "Selected payments have been marked as failed.")

    mark_as_completed.short_description = "Mark selected payments as completed"
    mark_as_failed.short_description = "Mark selected payments as failed"


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """
    Admin panel for tracking refunds.
    """
    list_display = ("id", "client", "payment", "amount", "refund_method", "status", "processed_at")
    list_filter = ("status", "refund_method")
    search_fields = ("payment__transaction_id", "client__username")
    ordering = ("-processed_at",)
    readonly_fields = ("payment", "client", "amount", "refund_method", "processed_by", "processed_at")


@admin.register(PaymentDispute)
class PaymentDisputeAdmin(admin.ModelAdmin):
    """
    Admin panel for managing payment disputes.
    """
    list_display = ("id", "client", "payment", "reason", "status", "created_at", "resolved_at")
    list_filter = ("status",)
    search_fields = ("client__username", "payment__transaction_id")
    ordering = ("-created_at",)
    readonly_fields = ("client", "payment", "reason", "created_at", "resolved_at")
    actions = ["mark_as_resolved"]

    def mark_as_resolved(self, request, queryset):
        queryset.update(status="resolved", resolved_at=timezone.now())
        self.message_user(request, "Selected disputes have been marked as resolved.")

    mark_as_resolved.short_description = "Mark selected disputes as resolved"


@admin.register(PaymentNotification)
class PaymentNotificationAdmin(admin.ModelAdmin):
    """
    Admin panel for viewing payment notifications.
    """
    list_display = ("user", "payment", "message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "payment__transaction_id")
    ordering = ("-created_at",)


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    """
    Admin panel for tracking all payment-related logs.
    """
    list_display = ("payment", "event", "timestamp", "details")
    list_filter = ("event", "timestamp")
    search_fields = ("payment__transaction_id", "event")
    ordering = ("-timestamp",)


# @admin.register(DiscountUsage)
# class DiscountUsageAdmin(admin.ModelAdmin):
#     """
#     Admin panel for tracking discount usage by clients.
#     """
#     list_display = ("discount", "user", "order", "special_order", "applied_at")
#     list_filter = ("discount", "applied_at")
#     search_fields = ("user__username", "discount__code")
#     ordering = ("-applied_at",)


@admin.register(SplitPayment)
class SplitPaymentAdmin(admin.ModelAdmin):
    """
    Admin panel for managing split payments.
    """
    list_display = ("payment", "method", "amount", "created_at")
    list_filter = ("method",)
    search_fields = ("payment__transaction_id",)
    ordering = ("-created_at",)


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    """
    Admin panel for tracking admin actions on payments, disputes, and refunds.
    """
    list_display = ("admin", "action", "timestamp", "details")
    list_filter = ("action", "timestamp")
    search_fields = ("admin__username", "action")
    ordering = ("-timestamp",)


@admin.register(PaymentReminderSettings)
class PaymentReminderSettingsAdmin(admin.ModelAdmin):
    """
    Admin panel for managing payment reminder settings.
    """
    list_display = ("first_reminder_hours", "final_reminder_hours", "last_updated")
    ordering = ("-last_updated",)
    fields = (
        "first_reminder_hours", "final_reminder_hours",
        "first_reminder_message", "final_reminder_message"
    )