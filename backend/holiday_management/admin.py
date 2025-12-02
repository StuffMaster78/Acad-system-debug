"""
Holiday Management Admin
"""
from django.contrib import admin
from .models import SpecialDay, HolidayReminder, HolidayDiscountCampaign


@admin.register(SpecialDay)
class SpecialDayAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type', 'date', 'is_annual', 'is_international', 'priority', 'is_active')
    list_filter = ('event_type', 'is_annual', 'is_international', 'priority', 'is_active', 'auto_generate_discount')
    search_fields = ('name', 'description')
    # Countries stored as JSONField, not ManyToMany
    readonly_fields = ('created_at', 'updated_at')


@admin.register(HolidayReminder)
class HolidayReminderAdmin(admin.ModelAdmin):
    list_display = ('special_day', 'reminder_date', 'status', 'broadcast_sent', 'discount_created', 'created_at')
    list_filter = ('status', 'broadcast_sent', 'discount_created', 'reminder_date')
    search_fields = ('special_day__name', 'notes')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(HolidayDiscountCampaign)
class HolidayDiscountCampaignAdmin(admin.ModelAdmin):
    list_display = ('special_day', 'year', 'discount', 'is_active', 'auto_generated', 'created_at')
    list_filter = ('is_active', 'auto_generated', 'year')
    search_fields = ('special_day__name', 'discount__code')
    readonly_fields = ('created_at',)

