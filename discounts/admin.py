from django.contrib import admin
from .models import Discount, SeasonalEvent

@admin.register(SeasonalEvent)
class SeasonalEventAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_active")
    list_filter = ("is_active", "start_date", "end_date")
    search_fields = ("name",)
    ordering = ("-start_date",)

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "value", "is_active", "used_count", "max_uses", "start_date", "end_date", "assigned_to_client", "seasonal_event")
    list_filter = ("is_active", "discount_type", "seasonal_event", "start_date", "end_date")
    search_fields = ("code", "assigned_to_client__email")  # Search by code or client email
    ordering = ("-start_date",)
    readonly_fields = ("used_count",)
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("code", "description", "discount_type", "value", "is_active"),
        }),
        ("Usage Restrictions", {
            "fields": ("max_uses", "used_count", "min_order_value"),
        }),
        ("Availability", {
            "fields": ("start_date", "end_date", "seasonal_event"),
        }),
        ("Target Audience", {
            "fields": ("is_general", "assigned_to_client"),
        }),
    )

    def deactivate_expired_discounts(self, request, queryset):
        """Admin action to deactivate expired discounts."""
        queryset.update(is_active=False)
    deactivate_expired_discounts.short_description = "Deactivate selected expired discounts"

    actions = [deactivate_expired_discounts]