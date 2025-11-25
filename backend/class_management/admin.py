from django.contrib import admin
from django.utils.html import format_html
from decimal import Decimal
from class_management.models import (
    ExpressClass,
    ClassDurationOption,
    ClassBundleConfig,
    ClassBundle,
)


@admin.register(ClassDurationOption)
class ClassDurationOptionAdmin(admin.ModelAdmin):
    list_display = ('website', 'class_code', 'label', 'is_active')
    list_filter = ('website', 'is_active')
    search_fields = ('class_code', 'label', 'website__name')
    list_editable = ('is_active',)
    ordering = ('website', 'class_code')


@admin.register(ClassBundleConfig)
class ClassBundleConfigAdmin(admin.ModelAdmin):
    list_display = (
        'website', 'level', 'duration', 'bundle_size', 
        'price_per_class', 'total_price_display', 'is_active'
    )
    list_filter = ('website', 'level', 'duration', 'is_active', 'bundle_size')
    search_fields = ('website__name', 'duration__label', 'duration__class_code')
    list_editable = ('is_active', 'price_per_class')
    ordering = ('website', 'level', 'duration', 'bundle_size')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('website', 'duration', 'level', 'bundle_size', 'is_active')
        }),
        ('Pricing', {
            'fields': ('price_per_class', 'total_price_display'),
            'description': 'Total price is calculated automatically: bundle_size × price_per_class'
        }),
    )
    readonly_fields = ('total_price_display',)
    
    def total_price_display(self, obj):
        """Display calculated total price"""
        if obj.pk:
            total = obj.total_price
            return format_html(
                '<strong style="color: #28a745;">${}</strong>',
                f'{total:,.2f}'
            )
        return '—'
    total_price_display.short_description = 'Total Bundle Price'


@admin.register(ClassBundle)
class ClassBundleAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'client', 'website', 'level', 'bundle_size', 
        'status', 'total_price', 'pricing_source', 'assigned_writer', 'created_at'
    )
    list_filter = (
        'website', 'status', 'level', 'pricing_source', 
        'created_at', 'start_date'
    )
    search_fields = (
        'client__username', 'client__email', 
        'assigned_writer__username', 'assigned_writer__email',
        'config__duration__label'
    )
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('client', 'website', 'status', 'assigned_writer')
        }),
        ('Configuration', {
            'fields': ('config', 'pricing_source', 'level', 'duration', 'bundle_size')
        }),
        ('Class Details', {
            'fields': (
                'number_of_classes', 'start_date', 'end_date'
            )
        }),
        ('Pricing', {
            'fields': (
                'price_per_class', 'total_price', 'original_price', 
                'discount', 'deposit_required', 'deposit_paid', 'balance_remaining'
            )
        }),
        ('Payment Options', {
            'fields': (
                'installments_enabled', 'installment_count'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


@admin.register(ExpressClass)
class ExpressClassAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'client', 'website', 'course', 'discipline', 
        'status', 'price', 'assigned_writer', 'created_at'
    )
    list_filter = ('status', 'website', 'academic_level', 'created_at')
    search_fields = ('client__username', 'client__email', 'course', 'institution', 'discipline')
    readonly_fields = ('created_at', 'updated_at', 'reviewed_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('client', 'website', 'status', 'assigned_writer')
        }),
        ('Class Details', {
            'fields': (
                'start_date', 'end_date', 'discipline', 'institution', 
                'course', 'academic_level'
            )
        }),
        ('Workload', {
            'fields': (
                'number_of_discussion_posts', 'number_of_discussion_posts_replies',
                'number_of_assignments', 'number_of_exams', 'number_of_quizzes',
                'number_of_projects', 'number_of_presentations', 'number_of_papers',
                'total_workload_in_pages'
            )
        }),
        ('Pricing', {
            'fields': ('price', 'price_approved', 'installments_needed')
        }),
        ('School Login', {
            'fields': ('school_login_link', 'school_login_username', 'school_login_password')
        }),
        ('Admin Review', {
            'fields': (
                'scope_review_notes', 'admin_notes', 
                'reviewed_by', 'reviewed_at'
            )
        }),
        ('Instructions', {
            'fields': ('instructions',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'is_complete')
        }),
    )
