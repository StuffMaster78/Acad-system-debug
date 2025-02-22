from django.contrib import admin
from .models import LoyaltyTier, LoyaltyTransaction, Milestone, ClientBadge

@admin.register(LoyaltyTier)
class LoyaltyTierAdmin(admin.ModelAdmin):
    list_display = ['name', 'threshold', 'discount_percentage', 'website']


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ['client', 'points', 'transaction_type', 'timestamp']
    search_fields = ['client__user__username']
    list_filter = ['transaction_type', 'timestamp']


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'target_type', 'target_value', 'reward_points']


@admin.register(ClientBadge)
class ClientBadgeAdmin(admin.ModelAdmin):
    list_display = ['client', 'badge_name', 'awarded_at']