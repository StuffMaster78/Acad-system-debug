from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'topic', 'client', 'status', 'total_price', 'subject', 'client_deadline', 'date_posted')
    list_filter = ('status', 'is_high_value', 'is_urgent', 'website')
    search_fields = ('title', 'topic', 'instructions', 'client__email', 'assigned_writer__email')
    ordering = ('-date_posted',)
    readonly_fields = ('date_posted', 'completed_at', 'total_price', 'payment_status')
    fieldsets = (
        ('Order Details', {
            'fields': ('title', 'topic', 'instructions', 'academic_level', 'type_of_work', 'number_of_pages', 'number_of_slides')
        }),
        ('Deadlines', {
            'fields': ('client_deadline', 'writer_deadline')
        }),
        ('Pricing and Payments', {
            'fields': ('total_price', 'additional_services', 'discount_code', 'tips', 'payment_status')
        }),
        ('Status and Flags', {
            'fields': ('status', 'revision_requested', 'is_high_value', 'is_urgent')
        }),
        ('Relationships', {
            'fields': ('client', 'assigned_writer')
        }),
        ('Timestamps', {
            'fields': ('date_posted', 'completed_at')
        }),
    )