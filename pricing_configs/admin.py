from django.contrib import admin
from .models import PricingConfiguration, AdditionalService, AcademicLevelPricing
from django.contrib.postgres.fields import JSONField  # if using Postgres
from django.db import models
from django.forms import widgets

@admin.register(PricingConfiguration)
class PricingConfigurationAdmin(admin.ModelAdmin):
    list_display = ["website", "created_at"]
    list_filter = ["website"]
    readonly_fields = ["created_at"]

    formfield_overrides = {
        models.JSONField: {
            "widget": widgets.Textarea(attrs={"rows": 10, "cols": 80})
        },
    }

@admin.register(AdditionalService)
class AdditionalServiceAdmin(admin.ModelAdmin):
    list_display = ('cost', 'is_active', 'website')
    list_filter = ('is_active', 'website')
    search_fields = ('website__name',)


@admin.register(AcademicLevelPricing)
class AcademicLevelPricingAdmin(admin.ModelAdmin):
    list_display = ('website', 'multiplier', 'created_at', 'updated_at')
    search_fields = ('website__name',)
    list_filter = ('website',)
    ordering = ['website']