"""
Admin interface for SEO Pages.
"""
from django.contrib import admin
from .models import SeoPage


@admin.register(SeoPage)
class SeoPageAdmin(admin.ModelAdmin):
    """Admin interface for SEO Pages."""
    
    list_display = [
        'title', 'slug', 'website', 'is_published', 
        'publish_date', 'created_at', 'updated_at'
    ]
    list_filter = [
        'website', 'is_published', 'is_deleted', 
        'publish_date', 'created_at'
    ]
    search_fields = ['title', 'slug', 'meta_title', 'meta_description']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('website', 'title', 'slug')
        }),
        ('SEO Metadata', {
            'fields': ('meta_title', 'meta_description')
        }),
        ('Content', {
            'fields': ('blocks',),
            'description': 'JSON array of content blocks (paragraph, heading, image, CTA, etc.)'
        }),
        ('Publication', {
            'fields': ('is_published', 'publish_date')
        }),
        ('Audit', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Soft Delete', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('website', 'created_by', 'updated_by')
    
    def save_model(self, request, obj, form, change):
        """Set created_by/updated_by automatically."""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

