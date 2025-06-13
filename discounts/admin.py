from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.timezone import now


from .models.promotions import PromotionalCampaign
from .models.discount import Discount, DiscountUsage
from .models.stacking import DiscountStackingRule

import random
import string
from django.utils.timezone import now
from django.contrib.admin import SimpleListFilter
from django.contrib.admin import TabularInline

class DiscountInline(admin.TabularInline):
    model = Discount
    fields = ('code', 'discount_type', 'value', 'is_active')
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
        'code', 'website', 'discount_type', 'value', 'is_active',
        'origin_type', 'start_date', 'end_date'
    )
    list_filter = (
        'website', 'discount_type', 'origin_type', 'is_active',
        'applies_to_first_order_only', DiscountStatusFilter
    )
    inlines = [DiscountStackingRuleInline]
    search_fields = ('code', 'description')
    autocomplete_fields = ('assigned_to_client', 'seasonal_event')
    filter_horizontal = ('stackable_with',)
    readonly_fields = ('used_count',)
    date_hierarchy = 'start_date'
    actions = ['deactivate_discounts', 'duplicate_discounts']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'assigned_to_client', 'seasonal_event'
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
                discount.code + "_" +
                ''.join(random.choices(string.ascii_uppercase, k=4))
            )
            discount.pk = None
            discount.code = new_code
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
        'user', 'website', 'base_discount',
        'stackable_with', 'used_at'
    )
    list_filter = ('website', 'base_discount')
    search_fields = (
        'user__email',
        'base_discount__code',
        'stackable_with__code'
    )
    autocomplete_fields = ('user', 'base_discount', 'stackable_with')


@admin.register(DiscountStackingRule)
class DiscountStackingRuleAdmin(admin.ModelAdmin):
    list_display = ('base_discount', 'stackable_with')
    search_fields = (
        'base_discount__code',
        'stackable_with__code'
    )
    autocomplete_fields = ('base_discount', 'stackable_with')


@admin.register(PromotionalCampaign)
class PromotionalCampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    search_fields = ('name',)
    date_hierarchy = 'start_date'
    inlines = [DiscountInline]
