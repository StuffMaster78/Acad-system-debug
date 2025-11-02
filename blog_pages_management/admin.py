from django.contrib import admin
from .models import (
    BlogCategory, BlogTag, BlogResource, BlogFAQ, AuthorProfile,
    BlogPost, BlogClick, BlogConversion, NewsletterSubscriber,
    Newsletter, NewsletterAnalytics, NewsletterCategory,
    BlogMediaFile, BlogVideo, BlogDarkModeImage,
    BlogABTest, SocialPlatform, BlogShare,
    AdminNotification, BlogActionLog
)
from .models.pdf_samples import (
    PDFSampleSection, PDFSample, PDFSampleDownload
)
from .models.draft_editing import (
    BlogPostRevision, BlogPostAutoSave, BlogPostEditLock, BlogPostPreview
)
from .models.workflow_models import (
    BlogPostWorkflow, BlogPostReviewComment, WorkflowTransition,
    ContentTemplate, ContentSnippet
)
from .models.analytics_models import (
    EditorAnalytics, BlogPostAnalytics, ContentPerformanceMetrics
)
from .models.security_models import (
    PreviewTokenRateLimit, AuditTrail
)

from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django.contrib import admin

# admin.site.register(PeriodicTask)
# admin.site.register(IntervalSchedule)
# admin.site.register(CrontabSchedule)



@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "slug", "post_count", "total_views", "is_featured", "is_active")
    search_fields = ("name", "meta_title", "meta_description")
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("website", "is_featured", "is_active", "created_at")
    readonly_fields = ("post_count", "total_views", "total_conversions", "created_at", "updated_at")
    fieldsets = (
        ("Basic Information", {
            "fields": ("website", "name", "slug", "description")
        }),
        ("SEO", {
            "fields": ("meta_title", "meta_description", "category_image")
        }),
        ("Analytics", {
            "fields": ("post_count", "total_views", "total_conversions")
        }),
        ("Display", {
            "fields": ("display_order", "is_featured", "is_active")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )
    
    actions = ["update_analytics"]
    
    def update_analytics(self, request, queryset):
        """Admin action to update analytics for selected categories."""
        updated = 0
        for category in queryset:
            category.update_analytics()
            updated += 1
        self.message_user(request, f"Updated analytics for {updated} categories.")
    update_analytics.short_description = "Update analytics for selected categories"


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


# PDF Sample Admin
@admin.register(PDFSampleSection)
class PDFSampleSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "blog", "display_order", "is_active", "requires_auth", "pdf_samples_count")
    search_fields = ("title", "description", "blog__title")
    list_filter = ("is_active", "requires_auth", "blog__website")
    ordering = ("blog", "display_order")
    
    def pdf_samples_count(self, obj):
        return obj.pdf_samples.filter(is_active=True).count()
    pdf_samples_count.short_description = "Active PDFs"


@admin.register(PDFSample)
class PDFSampleAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "file_size_human", "download_count", "is_featured", "is_active", "uploaded_by")
    search_fields = ("title", "description", "section__title", "section__blog__title")
    list_filter = ("is_active", "is_featured", "section__blog__website", "created_at")
    readonly_fields = ("file_size", "download_count", "uploaded_by", "created_at", "updated_at")
    ordering = ("section", "is_featured", "display_order")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("section", "title", "description", "pdf_file")
        }),
        ("Display", {
            "fields": ("display_order", "is_featured", "is_active")
        }),
        ("Analytics", {
            "fields": ("file_size", "file_size_human", "download_count")
        }),
        ("Metadata", {
            "fields": ("uploaded_by", "created_at", "updated_at")
        }),
    )
    
    def file_size_human(self, obj):
        return obj.file_size_human
    file_size_human.short_description = "File Size"
    
    actions = ["reset_download_count"]
    
    def reset_download_count(self, request, queryset):
        """Reset download count for selected PDFs."""
        updated = queryset.update(download_count=0)
        self.message_user(request, f"Reset download count for {updated} PDFs.")
    reset_download_count.short_description = "Reset download count"


@admin.register(PDFSampleDownload)
class PDFSampleDownloadAdmin(admin.ModelAdmin):
    list_display = ("pdf_sample", "user", "ip_address", "downloaded_at")
    search_fields = ("pdf_sample__title", "user__username", "ip_address")
    list_filter = ("downloaded_at", "pdf_sample__section__blog__website")
    readonly_fields = ("downloaded_at",)
    ordering = ("-downloaded_at",)
    
    def has_add_permission(self, request):
        """Downloads are auto-created, not manually added."""
        return False


# Draft & Editing Admin
@admin.register(BlogPostRevision)
class BlogPostRevisionAdmin(admin.ModelAdmin):
    list_display = ("blog", "revision_number", "created_by", "created_at", "is_current", "change_summary")
    search_fields = ("blog__title", "created_by__username", "change_summary")
    list_filter = ("is_current", "created_at", "blog__website")
    readonly_fields = ("revision_number", "created_at")
    ordering = ("-created_at",)
    
    fieldsets = (
        ("Blog & Revision", {
            "fields": ("blog", "revision_number", "is_current")
        }),
        ("Content", {
            "fields": ("title", "content", "meta_title", "meta_description")
        }),
        ("Relationships", {
            "fields": ("authors_data", "tags_data", "category_id")
        }),
        ("Metadata", {
            "fields": ("created_by", "created_at", "change_summary")
        }),
    )


@admin.register(BlogPostAutoSave)
class BlogPostAutoSaveAdmin(admin.ModelAdmin):
    list_display = ("blog", "saved_by", "saved_at", "is_recovered")
    search_fields = ("blog__title", "saved_by__username")
    list_filter = ("is_recovered", "saved_at", "blog__website")
    readonly_fields = ("saved_at",)
    ordering = ("-saved_at",)


@admin.register(BlogPostEditLock)
class BlogPostEditLockAdmin(admin.ModelAdmin):
    list_display = ("blog", "locked_by", "locked_at", "expires_at", "is_active", "is_expired")
    search_fields = ("blog__title", "locked_by__username")
    list_filter = ("is_active", "locked_at", "blog__website")
    readonly_fields = ("locked_at",)
    ordering = ("-locked_at",)
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = "Expired"


@admin.register(BlogPostPreview)
class BlogPostPreviewAdmin(admin.ModelAdmin):
    list_display = ("blog", "token_short", "created_by", "expires_at", "is_active", "view_count", "is_expired")
    search_fields = ("blog__title", "token", "created_by__username")
    list_filter = ("is_active", "created_at", "blog__website")
    readonly_fields = ("token", "created_at", "view_count")
    ordering = ("-created_at",)
    
    def token_short(self, obj):
        return obj.token[:16] + "..." if len(obj.token) > 16 else obj.token
    token_short.short_description = "Token"
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = "Expired"