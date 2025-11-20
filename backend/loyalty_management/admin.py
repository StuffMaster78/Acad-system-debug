from django.contrib import admin
from .models import (
    LoyaltyTier, LoyaltyTransaction, Milestone, ClientBadge,
    LoyaltyPointsConversionConfig,
    RedemptionCategory, RedemptionItem, RedemptionRequest,
    LoyaltyAnalytics, DashboardWidget
)

@admin.register(LoyaltyTier)
class LoyaltyTierAdmin(admin.ModelAdmin):
    list_display = ['name', 'threshold', 'discount_percentage', 'website']
    list_filter = ['website']
    search_fields = ['name']


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ['client', 'points', 'transaction_type', 'timestamp', 'redemption_request']
    search_fields = ['client__user__username']
    list_filter = ['transaction_type', 'timestamp', 'website']
    readonly_fields = ['timestamp']


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'target_type', 'target_value', 'reward_points', 'website']
    list_filter = ['target_type', 'website']
    search_fields = ['name']


@admin.register(ClientBadge)
class ClientBadgeAdmin(admin.ModelAdmin):
    list_display = ['client', 'badge_name', 'website', 'awarded_at']
    list_filter = ['website', 'badge_name']
    search_fields = ['client__user__username', 'badge_name']


@admin.register(LoyaltyPointsConversionConfig)
class LoyaltyPointsConversionConfigAdmin(admin.ModelAdmin):
    list_display = ['website', 'points_per_dollar', 'conversion_rate', 'min_conversion_points', 'active']
    list_filter = ['active', 'website']
    readonly_fields = ['website']


@admin.register(RedemptionCategory)
class RedemptionCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'is_active', 'sort_order', 'created_at']
    list_filter = ['website', 'is_active']
    search_fields = ['name']
    ordering = ['sort_order', 'name']


@admin.register(RedemptionItem)
class RedemptionItemAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'points_required', 'redemption_type',
        'stock_quantity', 'total_redemptions', 'is_active', 'website'
    ]
    list_filter = ['redemption_type', 'category', 'is_active', 'website']
    search_fields = ['name', 'description']
    readonly_fields = ['total_redemptions', 'created_at', 'updated_at']
    filter_horizontal = []


@admin.register(RedemptionRequest)
class RedemptionRequestAdmin(admin.ModelAdmin):
    list_display = [
        'client', 'item', 'points_used', 'status',
        'requested_at', 'approved_by', 'fulfilled_at'
    ]
    list_filter = ['status', 'item__category', 'website', 'requested_at']
    search_fields = ['client__user__username', 'item__name', 'fulfillment_code']
    readonly_fields = ['requested_at', 'approved_at', 'fulfilled_at', 'rejected_at']
    
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        """Bulk approve redemption requests."""
        count = 0
        for redemption in queryset.filter(status='pending'):
            try:
                from loyalty_management.services.redemption_service import RedemptionService
                RedemptionService.approve_redemption(redemption, request.user)
                count += 1
            except Exception as e:
                self.message_user(request, f"Error approving {redemption.id}: {str(e)}", level='error')
        self.message_user(request, f"Approved {count} redemption requests.")
    approve_requests.short_description = "Approve selected redemptions"
    
    def reject_requests(self, request, queryset):
        """Bulk reject redemption requests."""
        count = 0
        for redemption in queryset.filter(status='pending'):
            try:
                from loyalty_management.services.redemption_service import RedemptionService
                RedemptionService.reject_redemption(redemption, request.user, "Bulk rejection")
                count += 1
            except Exception as e:
                self.message_user(request, f"Error rejecting {redemption.id}: {str(e)}", level='error')
        self.message_user(request, f"Rejected {count} redemption requests.")
    reject_requests.short_description = "Reject selected redemptions"


@admin.register(LoyaltyAnalytics)
class LoyaltyAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'website', 'date_from', 'date_to', 'total_active_clients',
        'total_points_issued', 'total_points_redeemed', 'calculated_at'
    ]
    list_filter = ['website', 'calculated_at']
    readonly_fields = ['calculated_at', 'updated_at']
    date_hierarchy = 'date_to'


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['title', 'widget_type', 'website', 'position', 'is_visible']
    list_filter = ['widget_type', 'website', 'is_visible']
    search_fields = ['title']
    ordering = ['position']