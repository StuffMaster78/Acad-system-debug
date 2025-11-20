from django.contrib import admin
from .models import (
    SpecialOrder, 
    InstallmentPayment, 
    PredefinedSpecialOrderConfig, 
    PredefinedSpecialOrderDuration, 
    WriterBonus
)

@admin.register(SpecialOrder)
class SpecialOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'writer', 'order_type', 'status', 'total_cost', 'created_at')
    list_filter = ('status', 'order_type', 'created_at')
    search_fields = ('id', 'client__username', 'writer__username', 'predefined_type__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(InstallmentPayment)
class InstallmentPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'special_order', 'due_date', 'amount_due', 'is_paid')
    list_filter = ('is_paid', 'due_date')
    search_fields = ('special_order__id',)

@admin.register(PredefinedSpecialOrderConfig)
class PredefinedSpecialOrderConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'website', 'is_active')
    list_filter = ('is_active', 'website')
    search_fields = ('name', 'website__name')

@admin.register(PredefinedSpecialOrderDuration)
class PredefinedSpecialOrderDurationAdmin(admin.ModelAdmin):
    list_display = ('id', 'predefined_order', 'duration_days', 'price')
    list_filter = ('duration_days', 'predefined_order')
    search_fields = ('predefined_order__name',)

@admin.register(WriterBonus)
class WriterBonusAdmin(admin.ModelAdmin):
    list_display = ('id', 'writer', 'special_order', 'amount', 'category', 'is_paid', 'granted_at')
    list_filter = ('is_paid', 'category', 'granted_at')
    search_fields = ('writer__username', 'special_order__id')