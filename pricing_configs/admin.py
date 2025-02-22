from django.contrib import admin
from .models import PricingConfiguration, AdditionalService, AcademicLevelPricing


@admin.register(PricingConfiguration)
class PricingConfigurationAdmin(admin.ModelAdmin):
    list_display = ('website', 'base_price_per_page', 'base_price_per_slide', 'urgent_order_threshold')
    search_fields = ('website__name',)


@admin.register(AdditionalService)
class AdditionalServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'is_active', 'website')
    list_filter = ('is_active', 'website')
    search_fields = ('name', 'website__name')


@admin.register(AcademicLevelPricing)
class AcademicLevelPricingAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'multiplier', 'created_at', 'updated_at')
    search_fields = ('name', 'website__name')
    list_filter = ('website',)
    ordering = ['name']