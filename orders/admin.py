from django.contrib import admin
from .models import Order, Dispute, DisputeWriterResponse
from orders.models import PaymentTransaction
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'topic', 'client', 'writer', 'status', 
        'total_cost', 'subject', 'deadline', 'created_at'
    )
    list_filter = ('status', 'flag', 'website', 'is_paid', 'created_by_admin')
    search_fields = ('topic', 'instructions', 'client__email', 'writer__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'total_cost', 'writer_compensation', 'is_paid')
    
    fieldsets = (
        ('Order Details', {
            'fields': ('topic', 'instructions', 'paper_type', 'academic_level', 'formatting_style', 
                       'type_of_work', 'english_type', 'pages', 'slides', 'resources', 'spacing')
        }),
        ('Deadlines', {
            'fields': ('deadline', 'writer_deadline')
        }),
        ('Pricing and Payments', {
            'fields': ('total_cost', 'writer_compensation', 'extra_services', 
                       'discount_code', 'is_paid')
        }),
        ('Status and Flags', {
            'fields': ('status', 'flag', 'created_by_admin', 'is_special_order')
        }),
        ('Relationships', {
            'fields': ('client', 'writer', 'preferred_writer')
        }),
        ('Website and Timestamps', {
            'fields': ('website', 'created_at', 'updated_at')
        }),
    )

@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'raised_by', 'status', 'created_at')
    search_fields = ('order__id', 'raised_by__username', 'status')
    list_filter = ('status', 'created_at')
    actions = ['resolve_writer_wins', 'resolve_client_wins', 'extend_order', 'reassign_order']

    def resolve_writer_wins(self, request, queryset):
        for dispute in queryset:
            dispute.resolution_notes = "Writer wins dispute. Order completed."
            dispute.status = 'resolved'
            dispute.save()
    resolve_writer_wins.short_description = "Mark selected disputes as Writer Wins"

    def resolve_client_wins(self, request, queryset):
        for dispute in queryset:
            dispute.resolution_notes = "Client wins dispute. Order cancelled."
            dispute.status = 'resolved'
            dispute.save()
    resolve_client_wins.short_description = "Mark selected disputes as Client Wins"

    def extend_order(self, request, queryset):
        for dispute in queryset:
            dispute.resolution_notes = "Admin extended order deadline."
            dispute.status = 'resolved'
            dispute.order.status = 'revision'
            dispute.order.save()
            dispute.save()
    extend_order.short_description = "Extend Order Deadline"

    def reassign_order(self, request, queryset):
        for dispute in queryset:
            dispute.resolution_notes = "Admin reassigned the order."
            dispute.status = 'resolved'
            dispute.order.status = 'available'
            dispute.order.save()
            dispute.save()
    reassign_order.short_description = "Reassign Order"

@admin.register(DisputeWriterResponse)
class DisputeWriterResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'dispute', 'responded_by', 'timestamp')
    search_fields = ('dispute__id', 'responded_by__username')
    list_filter = ('timestamp',)



@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "order", "amount", "status", "date_processed")
    list_filter = ("status", "date_processed")
    search_fields = ("transaction_id", "order__id")
    actions = ["mark_as_completed", "mark_as_failed", "refund_transaction"]

    def mark_as_completed(self, request, queryset):
        queryset.update(status="completed")
    mark_as_completed.short_description = "Mark selected transactions as completed"

    def mark_as_failed(self, request, queryset):
        queryset.update(status="failed")
    mark_as_failed.short_description = "Mark selected transactions as failed"

    def refund_transaction(self, request, queryset):
        queryset.update(status="refunded")
    refund_transaction.short_description = "Mark selected transactions as refunded"