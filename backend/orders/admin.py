import json
from django import forms
from django.forms import widgets
from django.db import models
from django.utils.html import format_html
from django.contrib import admin
from .models import (
    Order, WriterProgress, Dispute,
    DisputeWriterResponse, WriterRequest,
    OrderTransitionLog,
    OrderPricingSnapshot
)
from orders.models import WebhookDeliveryLog
from orders.admin_filters import (
    StatusGroupFilter,
    CanTransitionToFilter,
    RecentlyTransitionedFilter,
    NeedsAttentionFilter,
    TransitionCountFilter,
)

class PrettyJSONWidget(widgets.Textarea):
    def format_value(self, value):
        if isinstance(value, dict):
            return json.dumps(value, indent=4)
        return super().format_value(value)

    def render(self, name, value, attrs=None, renderer=None):
        value = self.format_value(value)
        return super().render(name, value, attrs, renderer)
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'client', 'assigned_writer', 'topic',
        'status', 'client_deadline', 'is_paid', 'total_price',
        'writer_deadline', 'requires_editing', 'editing_skip_reason',
        'created_at', 'updated_at'
    )
    list_filter = (
        StatusGroupFilter,
        'status',
        CanTransitionToFilter,
        NeedsAttentionFilter,
        RecentlyTransitionedFilter,
        TransitionCountFilter,
        'is_paid',
        'requires_editing',
        'is_urgent',
        'created_at',
        'client_deadline',
        'website',
    )
    search_fields = ('id', 'client__username', 'writer__username', 'topic')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'editing_skip_reason')
    fieldsets = (
        ('Order Information', {
            'fields': (
                'client', 'assigned_writer', 'topic', 'status',
                'order_instructions', 'website'
            )
        }),
        ('Editing Settings', {
            'fields': (
                'requires_editing',
                'editing_skip_reason',
                'is_urgent',
            ),
            'description': (
                'requires_editing: None = use config rules, True = force editing, '
                'False = skip editing. Urgent orders automatically skip editing.'
            )
        }),
        ('Financial', {
            'fields': ('total_price', 'writer_compensation', 'is_paid')
        }),
        ('Deadlines', {
            'fields': ('client_deadline', 'writer_deadline')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_completed', 'cancel_order', 'force_editing', 'skip_editing']
    
    def force_editing(self, request, queryset):
        """Force editing for selected orders."""
        count = queryset.update(requires_editing=True)
        self.message_user(request, f"{count} order(s) will now undergo editing.")
    force_editing.short_description = "Force editing for selected orders"
    
    def skip_editing(self, request, queryset):
        """Skip editing for selected orders."""
        count = queryset.update(requires_editing=False, editing_skip_reason="Admin disabled editing")
        self.message_user(request, f"{count} order(s) will skip editing.")
    skip_editing.short_description = "Skip editing for selected orders"

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
    list_display = ['order', 'writer', 'progress_percentage', 'is_withdrawn', 'contains_screened_words', 'timestamp']
    list_filter = ['timestamp', 'is_withdrawn', 'contains_screened_words']
    search_fields = ('order__id', 'writer__username', 'notes')
    ordering = ('-timestamp',)
    readonly_fields = ['timestamp', 'updated_at', 'withdrawn_at', 'withdrawn_by']


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'order', 'raised_by', 'dispute_status',
        'resolution_outcome', 'created_at'
    )
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
    list_filter = (
        'is_automatic', 'old_status',
        'new_status', 'action', 'timestamp'
    )
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
    list_display = (
        "event", "user", "success",
        "status_code", "retry_count", "created_at"
    )
    list_filter = ("success", "event", "test_mode")
    search_fields = ("user__email", "event", "url")
    readonly_fields = ("request_payload", "response_body", "error_message")


@admin.register(OrderPricingSnapshot)
class OrderPricingSnapshotAdmin(admin.ModelAdmin):
    list_display = ["order", "calculated_at", "display_total"]
    list_filter = ["calculated_at"]
    readonly_fields = ["order", "pricing_data", "calculated_at"]
    search_fields = ["order__id"]

    formfield_overrides = {
        models.JSONField: {"widget": PrettyJSONWidget}
    }

    def display_total(self, obj):
        try:
            return f"${obj.pricing_data.get('final_total', 'N/A')}"
        except Exception:
            return "N/A"

    def has_add_permission(self, request):
        return False  # snapshots should only be created programmatically

    def has_change_permission(self, request, obj=None):
        return False  # immutable once saved

    def has_delete_permission(self, request, obj=None):
        return False