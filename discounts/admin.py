from django.contrib import admin
from .models import Discount

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'value', 'website', 'is_active', 'start_date', 'end_date', 'used_count', 'max_uses')
    list_filter = ('discount_type', 'is_active', 'website')
    search_fields = ('code', 'description')
    readonly_fields = ('used_count',)