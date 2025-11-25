from django.contrib import admin
from .models import WriterPayment, WriterPayoutRequest, SpecialOrderBonus, WriterPaymentAdjustment


@admin.register(WriterPayment)
class WriterPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'writer', 'order', 'special_order', 'amount', 
        'bonuses', 'tips', 'fines', 'status', 'processed_at', 'website'
    ]
    list_filter = ['status', 'website', 'processed_at']
    search_fields = [
        'writer__user__email', 'writer__user__username',
        'order__id', 'special_order__id', 'transaction_reference'
    ]
    readonly_fields = ['processed_at', 'updated_at']
    date_hierarchy = 'processed_at'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('website', 'writer', 'order', 'special_order', 'amount')
        }),
        ('Payment Components', {
            'fields': ('bonuses', 'tips', 'fines')
        }),
        ('Status', {
            'fields': ('status', 'transaction_reference', 'processed_at', 'updated_at')
        }),
    )


@admin.register(WriterPayoutRequest)
class WriterPayoutRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'writer', 'amount_requested', 'status', 
        'requested_at', 'processed_at', 'website'
    ]
    list_filter = ['status', 'website', 'requested_at']
    search_fields = ['writer__user__email', 'writer__user__username']
    readonly_fields = ['requested_at', 'processed_at']
    date_hierarchy = 'requested_at'


@admin.register(SpecialOrderBonus)
class SpecialOrderBonusAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'writer', 'special_order', 'bonus_amount', 
        'granted_at', 'website'
    ]
    list_filter = ['website', 'granted_at']
    search_fields = [
        'writer__user__email', 'special_order__id'
    ]
    readonly_fields = ['granted_at']
    date_hierarchy = 'granted_at'


@admin.register(WriterPaymentAdjustment)
class WriterPaymentAdjustmentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'writer_payment', 'admin', 'adjustment_amount', 
        'created_at', 'website'
    ]
    list_filter = ['website', 'created_at']
    search_fields = [
        'writer_payment__id', 'admin__email', 'admin__username', 'reason'
    ]
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
