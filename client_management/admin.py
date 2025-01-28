from django.contrib import admin
from .models import ClientProfile, LoyaltyTier, LoyaltyTransaction

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user", "website", "country", "timezone", "ip_address", "location_verified", "is_active"
    )
    list_filter = ("location_verified", "is_active", "country", "website")
    search_fields = ("user__username", "ip_address", "country", "website__name")

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "registration_id", "website", "loyalty_points", "tier", "is_active", "is_suspended")
    search_fields = ("user__username", "registration_id", "website__name")
    list_filter = ("is_active", "is_suspended", "website")

@admin.register(LoyaltyTier)
class LoyaltyTierAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "threshold", "discount_percentage")
    search_fields = ("name", "website__name")

@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ("client", "points", "transaction_type", "timestamp")
    search_fields = ("client__user__username",)
    list_filter = ("transaction_type",)