from django.contrib import admin
from orders.models import Order
from refunds.services import mark_order_refunded

@admin.action(description="Mark selected orders as refunded")
def mark_as_refunded(modeladmin, request, queryset):
    """
    Admin action to mark selected orders as refunded.
    """
    for order in queryset:
        mark_order_refunded(
            order,
            amount=order.total_amount,
            source='manual-admin'
        )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Extends admin interface to add refund capabilities.
    """
    list_display = ('id', 'status', 'cancelled', 'refunded_at')
    actions = [mark_as_refunded]