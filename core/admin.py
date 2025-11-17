"""
Admin interface for dashboard configuration
"""

from django.contrib import admin
from core.models.dashboard_config import DashboardCardConfig, DashboardFontConfig


@admin.register(DashboardCardConfig)
class DashboardCardConfigAdmin(admin.ModelAdmin):
    list_display = ['title', 'card_key', 'color', 'position', 'is_active', 'website']
    list_filter = ['is_active', 'color', 'data_type', 'website']
    search_fields = ['title', 'card_key', 'description']
    ordering = ['position', 'title']
    
    fieldsets = (
        ('Card Information', {
            'fields': ('card_key', 'title', 'description', 'icon', 'color', 'position', 'is_active')
        }),
        ('Data Configuration', {
            'fields': ('data_source', 'data_type', 'badge_text', 'config')
        }),
        ('Access Control', {
            'fields': ('allowed_roles', 'website')
        }),
    )
    
    filter_horizontal = []
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make allowed_roles a multiple choice field
        form.base_fields['allowed_roles'].help_text = 'Enter as JSON array, e.g., ["admin", "superadmin"]'
        return form


@admin.register(DashboardFontConfig)
class DashboardFontConfigAdmin(admin.ModelAdmin):
    list_display = ['website', 'font_family', 'base_font_size']
    list_filter = ['website']
    search_fields = ['font_family', 'website__name']
    
    fieldsets = (
        ('Website', {
            'fields': ('website',)
        }),
        ('Font Settings', {
            'fields': ('font_family', 'font_url', 'base_font_size', 'card_value_font_size', 'card_label_font_size')
        }),
    )

