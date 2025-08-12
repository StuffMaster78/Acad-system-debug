from django.contrib import admin
from .models import (
    CommunicationMessage, CommunicationThread, CommunicationNotification, 
    ScreenedWord, CommunicationLog, DisputeMessage, FlaggedMessage,
    MessageReadReceipt, SystemAlert, WebSocketAuditLog
)

@admin.register(CommunicationThread)
class OrderMessageThreadAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Order Message Threads.
    """
    list_display = (
        "id", "order", "is_active",
        "admin_override", "created_at",
        "updated_at"
    )
    list_filter = (
        "is_active", "admin_override",
        "created_at", "updated_at"
    )
    search_fields = ("id", "order__id",)
    actions = ["enable_messaging", "disable_messaging"]
    filter_horizontal = ("participants",)
    readonly_fields = ("created_at", "updated_at")

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


@admin.register(CommunicationMessage)
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


@admin.register(CommunicationNotification)
class CommunicationNotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for managing message notifications.
    """
    list_display = (
        "id", "recipient", "message",
        "notification_text", "is_read", "created_at"
        "read_at"
    )
    list_filter = ("is_read", "created_at", "read_at")
    search_fields = ("recipient__username", "message_id", "notification_text")
    actions = ["mark_as_read"]

    def recipient_username(self, obj):
        return obj.recipient.username if obj.recipient else "-"

    def message_id(self, obj):
        return obj.message.id if obj.message else "-"

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
    list_display = ("id", "word")
    search_fields = ("word",)
    actions = ["delete_selected"]


# @admin.register(CommunicationLog)
# class OrderMessageLogAdmin(admin.ModelAdmin):
#     """
#     Admin interface for viewing message logs.
#     """
#     list_display = ("order", "user", "action", "timestamp", "details")
#     list_filter = ("action", "timestamp")
#     search_fields = ("order__id", "user__username", "action", "details")



@admin.register(DisputeMessage)
class DisputeMessageAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Dispute Messages.
    Allows admins to view, resolve, and update disputes.
    """
    list_display = (
        "id", "order_id", "sender_username", "category_display",
        "status_display", "created_at", "resolved_at"
    )
    list_filter = ("status", "category", "created_at", "resolved_at")
    search_fields = ("order_message__message", "sender__username", "resolution_comment")
    actions = ["mark_as_resolved", "escalate_dispute"]
    readonly_fields = ("created_at", "resolved_at")

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



@admin.register(FlaggedMessage)
class FlaggedMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order_id",
        "sender_username",
        "category",
        "is_unblocked",
        "flagged_at",
        "reviewed_by",
        "reviewed_at"
    )
    list_filter = ("category", "is_unblocked", "flagged_at")
    search_fields = ("order_message__sender__username", "admin_comment")
    readonly_fields = ("flagged_at", "reviewed_by", "reviewed_at")

    def sender_username(self, obj):
        return obj.order_message.sender.username if obj.order_message else "-"

    def order_id(self, obj):
        return obj.order_message.thread.order.id if obj.order_message else "-"
    

@admin.register(MessageReadReceipt)
class MessageReadReceiptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "message_id",
        "user_username",
        "read_at"
    )
    search_fields = ("user__username", "message__id")
    list_filter = ("read_at",)
    readonly_fields = ("read_at",)

    def user_username(self, obj):
        return obj.user.username if obj.user else "-"

    def message_id(self, obj):
        return obj.message.id if obj.message else "-"
    
@admin.register(CommunicationLog)
class CommunicationLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_username",
        "order",
        "action",
        "created_at"
    )
    list_filter = ("action", "created_at")
    search_fields = ("user__username", "order__id", "details")
    readonly_fields = ("user", "order", "action", "details", "created_at")

    def user_username(self, obj):
        return obj.user.username if obj.user else "-"
    

@admin.register(SystemAlert)
class SystemAlertAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "severity", "category",
        "triggered_by", "acknowledged", "created_at"
    )
    list_filter = ("severity", "category", "acknowledged", "created_at")
    search_fields = ("title", "message", "triggered_by__username")
    readonly_fields = ("created_at",)

    actions = ["mark_as_acknowledged"]

    def mark_as_acknowledged(self, request, queryset):
        updated = queryset.update(acknowledged=True)
        self.message_user(request, f"{updated} alerts marked as acknowledged.")
    mark_as_acknowledged.short_description = "Mark selected alerts as acknowledged"


@admin.register(WebSocketAuditLog)
class WebSocketAuditLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "thread", "created_at")
    search_fields = ("user__username", "action", "thread__id")
    list_filter = ("action", "created_at")
    readonly_fields = ("user", "action", "thread", "payload", "created_at")
