from django.contrib import admin
from .models import Fine, FineAppeal, FinePolicy, FineStatus
from .models.late_fine_policy import LatenessFineRule
from .models.fine_type_config import FineTypeConfig


@admin.register(FineTypeConfig)
class FineTypeConfigAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name', 'calculation_type', 'fixed_amount', 'percentage',
        'website', 'active', 'is_system_defined', 'created_by', 'created_at'
    )
    list_filter = (
        'calculation_type', 'active', 'is_system_defined',
        'website', 'created_at'
    )
    search_fields = ('code', 'name', 'description')
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description', 'is_system_defined')
        }),
        ('Calculation', {
            'fields': (
                'calculation_type',
                'fixed_amount',
                'percentage',
                'base_amount',
                'min_amount',
                'max_amount',
            )
        }),
        ('Scope', {
            'fields': ('website', 'active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):
        """System-defined fine types cannot be deleted."""
        readonly = list(super().get_readonly_fields(request, obj))
        if obj and obj.is_system_defined == 'system':
            readonly.extend(['code', 'is_system_defined', 'calculation_type'])
        return readonly


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'order', 'fine_type', 'fine_type_config', 'amount', 'status',
        'imposed_at', 'issued_by', 'resolved'
    )
    list_filter = ('fine_type', 'fine_type_config', 'status', 'imposed_at', 'resolved')
    search_fields = ('order__id', 'order__topic', 'reason', 'fine_type_config__name', 'fine_type_config__code')
    readonly_fields = ('imposed_at', 'resolved_at')
    fieldsets = (
        ('Fine Information', {
            'fields': ('order', 'fine_type', 'fine_type_config', 'amount', 'reason', 'status')
        }),
        ('Issuance', {
            'fields': ('issued_by', 'imposed_at')
        }),
        ('Resolution', {
            'fields': (
                'resolved', 'resolved_at', 'resolved_reason',
                'waived_by', 'waived_at', 'waiver_reason'
            ),
            'classes': ('collapse',)
        }),
    )
    actions = ['waive_selected_fines', 'void_selected_fines']
    
    def waive_selected_fines(self, request, queryset):
        """Admin action to waive selected fines."""
        from fines.services.fine_services import FineService
        count = 0
        for fine in queryset.exclude(status__in=[FineStatus.WAIVED, FineStatus.VOIDED]):
            try:
                FineService.waive_fine(fine, request.user, "Bulk waiver by admin")
                count += 1
            except Exception:
                pass
        self.message_user(request, f"{count} fine(s) waived.")
    waive_selected_fines.short_description = "Waive selected fines"
    
    def void_selected_fines(self, request, queryset):
        """Admin action to void selected fines."""
        from fines.services.fine_services import FineService
        count = 0
        for fine in queryset.exclude(status__in=[FineStatus.WAIVED, FineStatus.VOIDED]):
            try:
                FineService.void_fine(fine, request.user, "Bulk void by admin")
                count += 1
            except Exception:
                pass
        self.message_user(request, f"{count} fine(s) voided.")
    void_selected_fines.short_description = "Void selected fines"


@admin.register(FineAppeal)
class FineAppealAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'fine', 'appealed_by', 'created_at',
        'reviewed_by', 'reviewed_at', 'accepted', 'escalated'
    )
    list_filter = ('accepted', 'escalated', 'created_at', 'reviewed_at')
    search_fields = ('fine__order__id', 'fine__order__topic', 'reason')
    readonly_fields = ('created_at', 'reviewed_at', 'escalated_at')
    fieldsets = (
        ('Appeal Information', {
            'fields': ('fine', 'reason', 'appealed_by', 'created_at')
        }),
        ('Review', {
            'fields': (
                'reviewed_by', 'reviewed_at', 'accepted',
                'resolution_notes'
            )
        }),
        ('Escalation', {
            'fields': ('escalated', 'escalated_at', 'escalated_to'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FinePolicy)
class FinePolicyAdmin(admin.ModelAdmin):
    list_display = (
        'fine_type', 'percentage', 'fixed_amount',
        'active', 'start_date', 'end_date'
    )
    list_filter = ('fine_type', 'active', 'start_date')
    search_fields = ('description',)
    date_hierarchy = 'start_date'


@admin.register(LatenessFineRule)
class LatenessFineRuleAdmin(admin.ModelAdmin):
    list_display = (
        'website', 'calculation_mode', 'first_hour_percentage',
        'second_hour_percentage', 'third_hour_percentage',
        'active', 'start_date'
    )
    list_filter = ('website', 'calculation_mode', 'active', 'start_date')
    search_fields = ('description', 'website__domain')
    fieldsets = (
        ('Website', {
            'fields': ('website', 'description')
        }),
        ('Calculation Mode', {
            'fields': ('calculation_mode', 'base_amount')
        }),
        ('Hourly Percentages', {
            'fields': (
                'first_hour_percentage',
                'second_hour_percentage',
                'third_hour_percentage',
                'subsequent_hours_percentage',
            )
        }),
        ('Daily Rate', {
            'fields': ('daily_rate_percentage',)
        }),
        ('Limits', {
            'fields': ('max_fine_percentage',)
        }),
        ('Activation', {
            'fields': ('active', 'start_date', 'end_date', 'created_by')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
