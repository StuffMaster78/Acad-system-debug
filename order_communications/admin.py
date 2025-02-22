from django.contrib import admin
from .models import (
    OrderMessage, OrderMessageThread, OrderMessageNotification, 
    ScreenedWord, OrderMessageLog, DisputeMessage
)

@admin.register(OrderMessageThread)
class OrderMessageThreadAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Order Message Threads.
    """
    list_display = ("order", "is_active", "admin_override", "created_at")
    list_filter = ("is_active", "admin_override")
    search_fields = ("order__id",)
    actions = ["enable_messaging", "disable_messaging"]

    def enable_messaging(self, request, queryset):
        """Allow admins to enable messaging for archived orders."""
        queryset.update(is_active=True, admin_override=True)
        self.message_user(request, "Selected threads have messaging enabled.")
    enable_messaging.short_description = "Enable messaging for selected orders"

    def disable_messaging(self, request, queryset):
        """Disable messaging for selected orders."""
        queryset.update(is_active=False, admin_override=False)
        self.message_user(request, "Selected threads have messaging disabled.")
    disable_messaging.short_description = "Disable messaging for selected orders"


@admin.register(OrderMessage)
class OrderMessageAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Order Messages.
    """
    list_display = ("id", "thread", "sender", "message", "sender_role", "sent_at", "is_read", "is_flagged", "is_unblocked")
    list_filter = ("is_flagged", "is_unblocked", "is_read", "sender_role")
    search_fields = ("message", "sender__username", "thread__order__id")
    actions = ["unblock_messages", "flag_messages"]

    def unblock_messages(self, request, queryset):
        """Allow admins to manually unblock messages."""
        queryset.update(is_flagged=False, is_unblocked=True)
        self.message_user(request, "Selected messages have been unblocked.")
    unblock_messages.short_description = "Unblock selected flagged messages"

    def flag_messages(self, request, queryset):
        """Manually flag messages (if necessary)."""
        queryset.update(is_flagged=True, is_unblocked=False)
        self.message_user(request, "Selected messages have been flagged for review.")
    flag_messages.short_description = "Flag selected messages for admin review"


@admin.register(OrderMessageNotification)
class OrderMessageNotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for managing message notifications.
    """
    list_display = ("recipient", "message", "notification_text", "is_read", "created_at")
    list_filter = ("is_read",)
    search_fields = ("recipient__username", "notification_text")
    actions = ["mark_as_read"]

    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read."""
        queryset.update(is_read=True)
        self.message_user(request, "Selected notifications marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"


@admin.register(ScreenedWord)
class ScreenedWordAdmin(admin.ModelAdmin):
    """
    Admin interface for managing banned words.
    """
    list_display = ("word",)
    search_fields = ("word",)
    actions = ["delete_selected"]


@admin.register(OrderMessageLog)
class OrderMessageLogAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing message logs.
    """
    list_display = ("order", "user", "action", "timestamp", "details")
    list_filter = ("action", "timestamp")
    search_fields = ("order__id", "user__username", "action", "details")



@admin.register(DisputeMessage)
class DisputeMessageAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Dispute Messages.
    Allows admins to view, resolve, and update disputes.
    """
    list_display = ("order_id", "sender_username", "category_display", "status_display", "created_at", "resolved_at")
    list_filter = ("status", "category", "created_at")
    search_fields = ("order_message__message", "sender__username", "resolution_comment")
    actions = ["mark_as_resolved", "escalate_dispute"]

    def order_id(self, obj):
        return obj.order_message.thread.order.id

    def sender_username(self, obj):
        return obj.sender.username

    def category_display(self, obj):
        return obj.get_category_display()

    def status_display(self, obj):
        return obj.get_status_display()

    def resolved_at(self, obj):
        return obj.resolved_at if obj.status == "resolved" else None

    def mark_as_resolved(self, request, queryset):
        """
        Admin action to mark disputes as resolved.
        """
        for dispute in queryset:
            dispute.resolve(admin_user=request.user, resolution_comment="Resolved by admin.")
        self.message_user(request, f"{queryset.count()} disputes marked as resolved.")

    def escalate_dispute(self, request, queryset):
        """
        Admin action to escalate unresolved disputes.
        """
        for dispute in queryset:
            if dispute.status == "pending":
                dispute.status = "escalated"
                dispute.save()
        self.message_user(request, f"{queryset.count()} disputes escalated.")

    mark_as_resolved.short_description = "Mark selected disputes as resolved"
    escalate_dispute.short_description = "Escalate selected disputes"
