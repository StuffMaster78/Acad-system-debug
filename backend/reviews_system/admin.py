from django.contrib import admin
from reviews_system.models.website_review import WebsiteReview
from reviews_system.models.writer_review import WriterReview
from reviews_system.models.order_review import OrderReview


@admin.register(WebsiteReview)
class WebsiteReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'reviewer', 'website', 'rating', 
        'is_approved', 'is_shadowed', 'is_flagged', 'submitted_at'
    )
    list_filter = (
        'is_approved', 'is_shadowed', 'is_flagged', 
        'rating', 'origin', 'website', 'submitted_at'
    )
    search_fields = (
        'reviewer__username', 'reviewer__email',
        'website__name', 'comment'
    )
    readonly_fields = ('submitted_at',)
    ordering = ('-submitted_at',)
    
    fieldsets = (
        ('Review Details', {
            'fields': ('reviewer', 'website', 'rating', 'comment', 'origin')
        }),
        ('Moderation', {
            'fields': ('is_approved', 'is_shadowed', 'is_flagged', 'flag_reason')
        }),
        ('Timestamps', {
            'fields': ('submitted_at',)
        }),
    )


@admin.register(WriterReview)
class WriterReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'reviewer', 'writer', 'website', 'rating',
        'is_approved', 'is_shadowed', 'is_flagged', 'submitted_at'
    )
    list_filter = (
        'is_approved', 'is_shadowed', 'is_flagged',
        'rating', 'origin', 'website', 'submitted_at'
    )
    search_fields = (
        'reviewer__username', 'reviewer__email',
        'writer__username', 'writer__email',
        'website__name', 'comment'
    )
    readonly_fields = ('submitted_at',)
    ordering = ('-submitted_at',)
    
    fieldsets = (
        ('Review Details', {
            'fields': ('reviewer', 'writer', 'website', 'rating', 'comment', 'origin')
        }),
        ('Moderation', {
            'fields': ('is_approved', 'is_shadowed', 'is_flagged', 'flag_reason')
        }),
        ('Timestamps', {
            'fields': ('submitted_at',)
        }),
    )


@admin.register(OrderReview)
class OrderReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'reviewer', 'order', 'writer', 'website', 'rating',
        'is_approved', 'is_shadowed', 'is_flagged', 'submitted_at'
    )
    list_filter = (
        'is_approved', 'is_shadowed', 'is_flagged',
        'rating', 'origin', 'website', 'submitted_at'
    )
    search_fields = (
        'reviewer__username', 'reviewer__email',
        'writer__username', 'writer__email',
        'order__id', 'website__name', 'comment'
    )
    readonly_fields = ('submitted_at',)
    ordering = ('-submitted_at',)
    
    fieldsets = (
        ('Review Details', {
            'fields': ('reviewer', 'order', 'writer', 'website', 'rating', 'comment', 'origin')
        }),
        ('Moderation', {
            'fields': ('is_approved', 'is_shadowed', 'is_flagged', 'flag_reason')
        }),
        ('Timestamps', {
            'fields': ('submitted_at',)
        }),
    )
