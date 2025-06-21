from django.contrib import admin
from .models import (
    Order, WriterProgress, Dispute,
    DisputeWriterResponse, WriterRequest,
    OrderTransitionLog
)
from orders.models import WebhookDeliveryLog


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'client', 'assigned_writer', 'topic',
        'status', 'client_deadline', 'is_paid', 'total_price',
        'writer_deadline', 'created_at', 'updated_at'
    )
    list_filter = ('status', 'is_paid', 'created_at', 'client_deadline')
    search_fields = ('id', 'client__username', 'writer__username', 'topic')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    actions = ['mark_as_completed', 'cancel_order']

    def mark_as_completed(self, request, queryset):
        for order in queryset:
            order.mark_as_completed(request.user)
        self.message_user(request, "Selected orders marked as completed.")
    mark_as_completed.short_description = "Mark selected orders as completed"

    def cancel_order(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, "Selected orders have been cancelled.")
    cancel_order.short_description = "Cancel selected orders"


@admin.register(WriterProgress)
class WriterProgressAdmin(admin.ModelAdmin):
    list_display = ['order', 'writer', 'progress', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ('order__id', 'writer__username')
    ordering = ('-timestamp',)


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'raised_by', 'dispute_status', 'resolution_outcome', 'created_at')
    list_filter = ('dispute_status', 'resolution_outcome', 'created_at')
    search_fields = ('order__id', 'raised_by__username')
    ordering = ('-created_at',)
    actions = ['resolve_dispute']

    def resolve_dispute(self, request, queryset):
        for dispute in queryset:
            if dispute.dispute_status != 'resolved':
                dispute.dispute_status = 'resolved'
                dispute.resolve_dispute_action()
                dispute.save()
        self.message_user(request, "Selected disputes marked as resolved.")
    resolve_dispute.short_description = "Mark selected disputes as resolved"


@admin.register(DisputeWriterResponse)
class DisputeWriterResponseAdmin(admin.ModelAdmin):
    list_display = ('dispute', 'responded_by', 'timestamp')
    search_fields = ('dispute__id', 'responded_by__username')
    ordering = ('-timestamp',)


@admin.register(WriterRequest)
class WriterRequestAdmin(admin.ModelAdmin):
    list_display = ('order', 'request_type', 'admin_approval', 'client_approval')
    list_filter = ('request_type', 'admin_approval', 'client_approval')

@admin.register(OrderTransitionLog)
class OrderTransitionLogAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'order', 'old_status', 'new_status', 'action',
        'is_automatic', 'user', 'timestamp'
    )
    list_filter = ('is_automatic', 'old_status', 'new_status', 'action', 'timestamp')
    search_fields = ('order__reference_code', 'user__email', 'action')
    readonly_fields = ('order', 'old_status', 'new_status', 'timestamp', 'user')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    actions = ['mark_as_manual']
    def mark_as_manual(self, request, queryset):
        for log in queryset:
            if log.is_automatic:
                log.is_automatic = False
                log.save()
        self.message_user(request, "Selected logs marked as manual.")
    mark_as_manual.short_description = "Mark selected logs as manual"

@admin.register(WebhookDeliveryLog)
class WebhookDeliveryLogAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "success", "status_code", "retry_count", "created_at")
    list_filter = ("success", "event", "test_mode")
    search_fields = ("user__email", "event", "url")
    readonly_fields = ("request_payload", "response_body", "error_message")
