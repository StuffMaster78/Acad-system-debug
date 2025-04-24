from django.contrib import admin
from .models import Refund, RefundLog, RefundReceipt


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'client', 'order_payment', 'status',
        'wallet_amount', 'external_amount', 'refund_method',
        'processed_by', 'processed_at'
    )
    list_filter = ('status', 'refund_method', 'type')
    search_fields = ('client__username', 'order_payment__id')
    readonly_fields = ('processed_at',)
    ordering = ('-processed_at',)


@admin.register(RefundLog)
class RefundLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'source', 'status', 'created_at')
    list_filter = ('status', 'source')
    search_fields = ('order__id',)
    ordering = ('-created_at',)


@admin.register(RefundReceipt)
class RefundReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'refund', 'reference_code', 'generated_at')
    search_fields = ('reference_code',)
    ordering = ('-generated_at',)