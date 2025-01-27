from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'topic', 'client', 'writer', 'status', 
        'total_cost', 'subject', 'deadline', 'created_at'
    )
    list_filter = ('status', 'flag', 'website', 'is_paid', 'created_by_admin')
    search_fields = ('topic', 'instructions', 'client__email', 'writer__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'total_cost', 'writer_compensation', 'is_paid')
    
    fieldsets = (
        ('Order Details', {
            'fields': ('topic', 'instructions', 'paper_type', 'academic_level', 'formatting_style', 
                       'type_of_work', 'english_type', 'pages', 'slides', 'resources', 'spacing')
        }),
        ('Deadlines', {
            'fields': ('deadline', 'writer_deadline')
        }),
        ('Pricing and Payments', {
            'fields': ('total_cost', 'writer_compensation', 'extra_services', 
                       'discount_code', 'is_paid')
        }),
        ('Status and Flags', {
            'fields': ('status', 'flag', 'created_by_admin', 'is_special_order')
        }),
        ('Relationships', {
            'fields': ('client', 'writer', 'preferred_writer')
        }),
        ('Website and Timestamps', {
            'fields': ('website', 'created_at', 'updated_at')
        }),
    )