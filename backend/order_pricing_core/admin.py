from django.contrib import admin
from django.db import models
from django.forms import widgets
from .models import AcademicLevelRate, ServiceAddon, WebsitePricingProfile

@admin.register(WebsitePricingProfile)
class WebsitePricingProfileAdmin(admin.ModelAdmin):
    list_display = ["website", "created_at", "updated_at"]
    list_filter = ["website"]
    readonly_fields = ["created_at"]

    formfield_overrides = {
        models.JSONField: {
            "widget": widgets.Textarea(attrs={"rows": 10, "cols": 80})
        },
    }

@admin.register(ServiceAddon)
class ServiceAddonAdmin(admin.ModelAdmin):
    list_display = ('name', 'flat_amount', 'is_active', 'website')
    list_filter = ('is_active', 'website')
    search_fields = ('name', 'website__name')


@admin.register(AcademicLevelRate)
class AcademicLevelPricingAdmin(admin.ModelAdmin):
    list_display = ('website', 'multiplier', 'created_at', 'updated_at')
    search_fields = ('website__name',)
    list_filter = ('website',)
    ordering = ['website']
