from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.timezone import now


from .models.promotions import PromotionalCampaign
from .models.discount import Discount, DiscountUsage
from .models.stacking import DiscountStackingRule
from .models.discount_configs import DiscountConfig

import random
import string
from django.utils.timezone import now
from django.contrib.admin import SimpleListFilter
from django.contrib.admin import TabularInline

class DiscountInline(admin.TabularInline):
    model = Discount
    fields = ('discount_code', 'discount_type', 'discount_value', 'is_active')
    extra = 1
    autocomplete_fields = ('assigned_to_client',)
class DiscountStackingRuleInline(admin.TabularInline):
    model = DiscountStackingRule
    fk_name = 'base_discount'
    extra = 1
    autocomplete_fields = ('stackable_with',)


class DiscountStatusFilter(SimpleListFilter):
    title = 'Discount Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('future', 'Upcoming')
        ]

    def queryset(self, request, queryset):
        current_time = now()
        if self.value() == 'active':
            return queryset.filter(
                is_active=True,
                start_date__lte=current_time,
                end_date__gte=current_time if queryset.filter(end_date__isnull=False).exists() else None
            )
        elif self.value() == 'expired':
            return queryset.filter(end_date__lt=current_time)
        elif self.value() == 'future':
            return queryset.filter(start_date__gt=current_time)
        return queryset

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = (
        'discount_code', 'website', 'discount_type', 'discount_value', 'is_active',
        'origin_type', 'start_date', 'end_date'
    )
    list_filter = (
        'website', 'discount_type', 'origin_type', 'is_active',
        'applies_to_first_order_only', DiscountStatusFilter
    )
    inlines = [DiscountStackingRuleInline]
    search_fields = ('discount_code', 'description')
    autocomplete_fields = ('assigned_to_client', 'promotional_campaign')
    readonly_fields = ('used_count',)
    date_hierarchy = 'start_date'
    actions = ['deactivate_discounts', 'duplicate_discounts']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'assigned_to_client', 'promotional_campaign', 'website'
        )

    @admin.action(description="Deactivate selected discounts")
    def deactivate_discounts(self, request, queryset):
        updated = queryset.update(is_active=False)
        messages.success(request, f"{updated} discount(s) deactivated.")

    @admin.action(description="Duplicate selected discounts for new season")
    def duplicate_discounts(self, request, queryset):
        new_discounts = []
        for discount in queryset:
            new_code = (
                discount.discount_code + "_" +
                ''.join(random.choices(string.ascii_uppercase, k=4))
            )
            discount.pk = None
            discount.discount_code = new_code
            discount.start_date = now()
            discount.end_date = None
            discount.is_active = True
            discount.used_count = 0
            new_discounts.append(discount)

        Discount.objects.bulk_create(new_discounts)
        messages.success(request, f"{len(new_discounts)} discount(s) duplicated.")


@admin.register(DiscountUsage)
class DiscountUsageAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'website', 'discount', 'used_at'
    )
    list_filter = ('website', 'discount')
    search_fields = (
        'user__email',
        'discount__discount_code'
    )
    autocomplete_fields = ('user', 'discount')


@admin.register(DiscountStackingRule)
class DiscountStackingRuleAdmin(admin.ModelAdmin):
    list_display = ('base_discount', 'stackable_with')
    search_fields = (
        'base_discount__discount_code',
        'stackable_with__discount_code'
    )
    autocomplete_fields = ('base_discount', 'stackable_with')


@admin.register(PromotionalCampaign)
class PromotionalCampaignAdmin(admin.ModelAdmin):
    list_display = ('campaign_name', 'start_date', 'end_date', 'is_active')
    search_fields = ('campaign_name',)
    date_hierarchy = 'start_date'
    inlines = [DiscountInline]


@admin.register(DiscountConfig)
class DiscountConfigAdmin(admin.ModelAdmin):
    """
    Admin interface for managing discount configuration settings per website.
    Allows superadmin and admin to set maximum discount caps, stacking rules,
    and other discount-related business rules.
    """
    list_display = (
        'website', 'max_stackable_discounts', 'max_discount_percent',
        'discount_threshold', 'enable_stacking', 'allow_stack_across_events',
        'updated_at'
    )
    list_filter = (
        'enable_stacking', 'allow_stack_across_events',
        'promotional_campaign_discount_active', 'website'
    )
    search_fields = ('website__name', 'website__domain')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    fieldsets = (
        ('Website', {
            'fields': ('website',)
        }),
        ('Stacking Configuration', {
            'fields': (
                'enable_stacking',
                'max_stackable_discounts',
                'allow_stack_across_events',
            ),
            'description': 'Control how many discounts can be stacked and whether cross-campaign stacking is allowed.'
        }),
        ('Discount Limits', {
            'fields': (
                'max_discount_percent',
                'discount_threshold',
            ),
            'description': 'Set maximum discount percentage per order and minimum order value for stacking.'
        }),
        ('Promotional Settings', {
            'fields': (
                'promotional_campaign_discount_active',
                'promotional_campaign_discount_value',
                'promotional_campaign',
            ),
            'classes': ('collapse',)
        }),
        ('User Experience', {
            'fields': ('enable_hints',),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    autocomplete_fields = ('website', 'promotional_campaign', 'created_by', 'updated_by')

    def save_model(self, request, obj, form, change):
        """
        Track who created/updated the discount config.
        """
        if not change:  # Creating new
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
