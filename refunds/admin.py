from django.contrib import admin
from .models import Refund, RefundLog, RefundReceipt
from refunds.tasks import retry_external_refund

@admin.action(description="Retry external refund via webhook")
def retry_selected_refunds(modeladmin, request, queryset):
    for refund in queryset.filter(
        status='pending', refund_method='external'
    ):
        retry_external_refund.delay(refund.id)

    modeladmin.message_user(
        request,
        f"{queryset.count()} refund(s) queued for retry."
    )

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'client', 'order_payment', 'status',
        'wallet_amount', 'external_amount', 'refund_method',
        'processed_by', 'processed_at'
    )
    actions = [retry_selected_refunds]
    list_filter = ('status', 'refund_method', 'type')
    search_fields = ('client__username', 'order_payment__id')
    readonly_fields = ('processed_at', 'processed_by', 'status')
    ordering = ('-processed_at',)
    date_hierarchy = 'processed_at'

@admin.register(RefundLog)
class RefundLogAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'order', 'amount', 'refund',
        'client', 'source', 'status', 'created_at'
    )
    list_filter = ('status', 'source')
    search_fields = ('order__id', 'refund__id', 'client__username')
    readonly_fields = (
        'created_at', 'processed_by', 'action',
        'metadata', 'client', 'refund', 'order',
        'amount', 'source', 'status'
    )
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    raw_id_fields = ('order', 'refund', 'client', 'processed_by')

@admin.register(RefundReceipt)
class RefundReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'refund', 'reference_code', 'generated_at')
    search_fields = ('reference_code',)
    ordering = ('-generated_at',)
    date_hierarchy = 'generated_at'
    readonly_fields = (
        'generated_at', 'refund', 'amount',
        'order_payment', 'client', 'processed_by', 'reason'
    )
    list_filter = ('refund__status', 'refund__refund_method')
    raw_id_fields = ('refund', 'order_payment', 'client', 'processed_by')
    fieldsets = (
        (None, {
            'fields': (
                'refund', 'reference_code', 'amount',
                'order_payment', 'client', 'processed_by', 'reason'
            )
        }),
        ('Timestamps', {
            'fields': ('generated_at',)
        }),
    )