from django.contrib import admin
from .models import WriterLevel, PaymentHistory, WriterProgress


@admin.register(WriterLevel)
class WriterLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_pay_per_page', 'max_orders', 'min_rating')
    search_fields = ('name',)
    list_filter = ('max_orders',)


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('writer', 'amount', 'payment_date', 'description')
    search_fields = ('writer__username',)
    list_filter = ('payment_date',)


@admin.register(WriterProgress)
class WriterProgressAdmin(admin.ModelAdmin):
    list_display = ('writer', 'order', 'progress', 'timestamp')
    search_fields = ('writer__username', 'order__id')
    list_filter = ('timestamp',)