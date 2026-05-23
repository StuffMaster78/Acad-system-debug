"""
Newsletter Admin
==================
"""

from django.contrib import admin

from cms_newsletters.models import (
    AutomationEnrollment,
    AutomationSequence,
    AutomationStep,
    Newsletter,
    NewsletterAnalytics,
    NewsletterEvent,
    Subscriber,
    SubscriberCategory,
)


@admin.register(SubscriberCategory)
class SubscriberCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "site"]
    list_filter = ["site"]


class AutomationStepInline(admin.TabularInline):
    model = AutomationStep
    extra = 0
    fields = ["step_order", "delay_days", "subject_line", "is_active"]


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "site",
        "is_active",
        "frequency",
        "source",
        "open_count",
        "click_count",
        "created_at",
    ]
    list_filter = ["site", "is_active", "source", "frequency"]
    search_fields = ["email"]
    date_hierarchy = "created_at"
    readonly_fields = [
        "open_count", "click_count",
        "last_opened_at", "last_clicked_at",
        "created_at", "updated_at",
    ]


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "site",
        "status",
        "category",
        "scheduled_send_date",
        "sent_at",
    ]
    list_filter = ["site", "status", "category"]
    search_fields = ["title", "subject_line"]


@admin.register(NewsletterEvent)
class NewsletterEventAdmin(admin.ModelAdmin):
    list_display = ["newsletter", "subscriber", "event_type", "subject_variant", "created_at"]
    list_filter = ["event_type", "subject_variant"]
    date_hierarchy = "created_at"
    readonly_fields = [
        "newsletter", "subscriber", "event_type",
        "link_url", "subject_variant", "created_at",
    ]

    def has_add_permission(self, request):
        return False


@admin.register(NewsletterAnalytics)
class NewsletterAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        "newsletter",
        "sent_count",
        "open_rate",
        "click_rate",
        "bounce_rate",
        "conversion_count",
        "conversion_revenue",
        "winning_subject",
    ]
    readonly_fields = [
        "newsletter", "sent_count", "delivered_count",
        "open_count", "open_rate", "click_count", "click_rate",
        "bounce_count", "bounce_rate", "complaint_count",
        "unsubscribe_count", "subject_a_open_rate",
        "subject_b_open_rate", "winning_subject",
        "conversion_count", "conversion_revenue", "computed_at",
    ]

    def has_add_permission(self, request):
        return False


@admin.register(AutomationSequence)
class AutomationSequenceAdmin(admin.ModelAdmin):
    list_display = ["name", "site", "trigger_type", "is_active"]
    list_filter = ["site", "trigger_type", "is_active"]
    inlines = [AutomationStepInline]


@admin.register(AutomationEnrollment)
class AutomationEnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        "subscriber",
        "sequence",
        "current_step",
        "status",
        "next_send_at",
        "enrolled_at",
    ]
    list_filter = ["status", "sequence"]
    readonly_fields = [
        "subscriber", "sequence", "current_step",
        "next_send_at", "enrolled_at", "completed_at",
    ]