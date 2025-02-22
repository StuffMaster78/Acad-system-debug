from django.contrib import admin
from .models import Order, WriterProgress, Dispute, DisputeWriterResponse

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'writer', 'topic', 'status', 'deadline', 'is_paid', 'total_cost')
    list_filter = ('status', 'is_paid', 'created_at', 'deadline')
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
    list_display = ('order', 'writer', 'progress', 'timestamp')
    list_filter = ('progress', 'timestamp')
    search_fields = ('order__id', 'writer__username')
    ordering = ('-timestamp',)


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'raised_by', 'status', 'resolution_outcome', 'created_at')
    list_filter = ('status', 'resolution_outcome', 'created_at')
    search_fields = ('order__id', 'raised_by__username')
    ordering = ('-created_at',)
    actions = ['resolve_dispute']

    def resolve_dispute(self, request, queryset):
        for dispute in queryset:
            if dispute.status != 'resolved':
                dispute.status = 'resolved'
                dispute.resolve_dispute_action()
                dispute.save()
        self.message_user(request, "Selected disputes marked as resolved.")
    resolve_dispute.short_description = "Mark selected disputes as resolved"


@admin.register(DisputeWriterResponse)
class DisputeWriterResponseAdmin(admin.ModelAdmin):
    list_display = ('dispute', 'responded_by', 'timestamp')
    search_fields = ('dispute__id', 'responded_by__username')
    ordering = ('-timestamp',)
