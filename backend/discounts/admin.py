from __future__ import annotations

from django.contrib import admin

from discounts.models import Discount
from discounts.models import DiscountSettings
from discounts.models import DiscountUsage
from discounts.models import FirstOrderDiscountConfig
from discounts.models import PromotionalCampaign


@admin.register(PromotionalCampaign)
class PromotionalCampaignAdmin(admin.ModelAdmin):
    """
    Admin configuration for promotional campaigns.
    """

    list_display = (
        "name",
        "website",
        "slug",
        "is_active",
        "is_archived",
        "starts_at",
        "ends_at",
        "created_at",
    )
    list_filter = (
        "website",
        "is_active",
        "is_archived",
        "starts_at",
        "ends_at",
    )
    search_fields = (
        "name",
        "slug",
        "description",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    """
    Admin configuration for client discount codes.
    """

    list_display = (
        "discount_code",
        "name",
        "website",
        "discount_type",
        "discount_value",
        "origin",
        "is_active",
        "is_archived",
        "starts_at",
        "ends_at",
        "created_at",
    )
    list_filter = (
        "website",
        "discount_type",
        "origin",
        "is_active",
        "is_archived",
        "is_deleted",
        "first_order_only",
    )
    search_fields = (
        "discount_code",
        "name",
        "description",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    filter_horizontal = (
        "eligible_clients",
    )


@admin.register(DiscountUsage)
class DiscountUsageAdmin(admin.ModelAdmin):
    """
    Admin read view for immutable discount usage records.
    """

    list_display = (
        "discount_code",
        "client",
        "website",
        "payable_type",
        "payable_id",
        "subtotal_amount",
        "discount_amount",
        "final_amount",
        "origin",
        "applied_at",
    )
    list_filter = (
        "website",
        "payable_type",
        "origin",
        "applied_at",
    )
    search_fields = (
        "discount_code",
        "payable_id",
        "client__email",
    )
    readonly_fields = (
        "website",
        "discount",
        "client",
        "payable_type",
        "payable_id",
        "discount_code",
        "discount_type",
        "discount_value",
        "subtotal_amount",
        "discount_amount",
        "final_amount",
        "origin",
        "metadata",
        "applied_at",
    )

    def has_add_permission(self, request) -> bool:
        """
        Prevent manual creation of usage records.
        """
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """
        Prevent mutation of usage records.
        """
        return False


@admin.register(DiscountSettings)
class DiscountSettingsAdmin(admin.ModelAdmin):
    """
    Admin configuration for tenant discount behavior.
    """

    list_display = (
        "website",
        "allow_manual_codes",
        "auto_apply_first_order_discount",
        "allow_code_to_replace_first_order",
        "auto_apply_best_discount",
        "updated_at",
    )
    list_filter = (
        "allow_manual_codes",
        "auto_apply_first_order_discount",
        "auto_apply_best_discount",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(FirstOrderDiscountConfig)
class FirstOrderDiscountConfigAdmin(admin.ModelAdmin):
    """
    Admin configuration for automatic first order discounts.
    """

    list_display = (
        "website",
        "is_enabled",
        "discount_type",
        "discount_value",
        "max_discount_amount",
        "min_payable_amount",
        "updated_at",
    )
    list_filter = (
        "is_enabled",
        "discount_type",
        "applies_to_orders",
        "applies_to_special_orders",
        "applies_to_class_bundles",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )