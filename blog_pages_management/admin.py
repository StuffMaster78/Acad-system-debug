from django.contrib import admin
from .models import (
    BlogCategory, BlogTag, BlogResource, BlogFAQ, AuthorProfile,
    BlogPost, BlogClick, BlogConversion, NewsletterSubscriber,
    Newsletter, NewsletterAnalytics, NewsletterCategory,
    BlogMediaFile, BlogVideo, BlogDarkModeImage,
    BlogABTest, SocialPlatform, BlogShare,
    AdminNotification, BlogActionLog
)

from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django.contrib import admin

# admin.site.register(PeriodicTask)
# admin.site.register(IntervalSchedule)
# admin.site.register(CrontabSchedule)



@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("website",)


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ("name", "website")
    search_fields = ("name",)
    list_filter = ("website",)


@admin.register(AuthorProfile)
class AuthorProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "designation", "is_fake")
    search_fields = ("name", "designation")
    list_filter = ("website", "is_fake")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "website", "category", "is_published", "publish_date", "click_count", "conversion_count")
    search_fields = ("title", "meta_title", "meta_description")
    list_filter = ("is_published", "category", "website", "created_at", "updated_at")
    date_hierarchy = "publish_date"
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ["authors", "tags", "category"]
    filter_horizontal = ["tags", "authors"]

    def get_queryset(self, request):
        """
        Optimizes queryset by selecting related fields for better performance.
        """
        return super().get_queryset(request).select_related("category", "website").prefetch_related("tags", "authors")


@admin.register(BlogClick)
class BlogClickAdmin(admin.ModelAdmin):
    list_display = ("blog", "user", "ip_address", "clicked_at")
    search_fields = ("blog__title", "user__email", "ip_address")
    list_filter = ("clicked_at",)


@admin.register(BlogConversion)
class BlogConversionAdmin(admin.ModelAdmin):
    list_display = ("blog", "user", "order_placed", "clicked_order_page", "converted_at")
    search_fields = ("blog__title", "user__email")
    list_filter = ("converted_at", "order_placed")


@admin.register(NewsletterCategory)
class NewsletterCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "website", "is_active", "subscription_type", "open_count")
    search_fields = ("email",)
    list_filter = ("subscription_type", "is_active", "website")


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("category", "subject_a", "is_sent", "scheduled_send_date", "sent_at")
    search_fields = ("subject_a", "subject_b")
    list_filter = ("is_sent", "scheduled_send_date")


@admin.register(NewsletterAnalytics)
class NewsletterAnalyticsAdmin(admin.ModelAdmin):
    list_display = ("newsletter", "version", "sent_count", "open_count", "click_count", "conversion_count")
    list_filter = ("version",)


@admin.register(BlogMediaFile)
class BlogMediaFileAdmin(admin.ModelAdmin):
    list_display = ("file", "file_type", "website", "uploaded_at")
    search_fields = ("file",)
    list_filter = ("file_type", "website", "uploaded_at")


@admin.register(BlogVideo)
class BlogVideoAdmin(admin.ModelAdmin):
    list_display = ("blog", "video_url", "source")
    search_fields = ("video_url",)
    list_filter = ("source",)


@admin.register(BlogDarkModeImage)
class BlogDarkModeImageAdmin(admin.ModelAdmin):
    list_display = ("blog", "website")
    list_filter = ("website",)


@admin.register(BlogABTest)
class BlogABTestAdmin(admin.ModelAdmin):
    list_display = ("blog", "headline_a", "headline_b", "winning_version")
    list_filter = ("winning_version",)


@admin.register(SocialPlatform)
class SocialPlatformAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "is_active", "is_disabled_by_owner")
    search_fields = ("name",)
    list_filter = ("is_active", "is_disabled_by_owner", "website")


@admin.register(BlogShare)
class BlogShareAdmin(admin.ModelAdmin):
    list_display = ("blog", "platform", "share_count", "last_shared_at")
    search_fields = ("blog__title", "platform__name")
    list_filter = ("platform", "website")


@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "is_read", "created_at")
    search_fields = ("user__email", "message")
    list_filter = ("is_read", "created_at")


@admin.register(BlogActionLog)
class BlogActionLogAdmin(admin.ModelAdmin):
    list_display = ("user", "blog", "action", "timestamp")
    search_fields = ("user__email", "blog__title", "action")
    list_filter = ("action", "timestamp")