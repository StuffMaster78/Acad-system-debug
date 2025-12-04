from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BlogPostViewSet, BlogCategoryViewSet, BlogTagViewSet,
    AuthorProfileViewSet, BlogClickViewSet, BlogConversionViewSet,
    RestoreSoftDeletedBlogView, PermanentlyDeleteBlogView,
    AdminNotificationsView, NewsletterSubscriberViewSet,
    NewsletterViewSet, NewsletterAnalyticsViewSet,
    BlogMediaFileViewSet, BlogVideoViewSet,
    BlogDarkModeImageViewSet, BlogABTestViewSet, 
    SocialPlatformViewSet, BlogShareViewSet
)
from .views.enhanced_views import (
    CTABlockViewSet,
    BlogCTAPlacementViewSet,
    ContentBlockTemplateViewSet,
    BlogContentBlockViewSet,
    BlogEditHistoryViewSet,
    BlogSEOMetadataViewSet,
    FAQSchemaViewSet,
    AuthorSchemaViewSet,
)
from .views.pdf_views import (
    PDFSampleSectionViewSet,
    PDFSampleViewSet,
    PDFSampleDownloadViewSet,
)
from .views.draft_views import (
    BlogPostRevisionViewSet,
    BlogPostAutoSaveViewSet,
    BlogPostEditLockViewSet,
    BlogPostPreviewViewSet,
)
from .views.workflow_views import (
    BlogPostWorkflowViewSet,
    BlogPostReviewCommentViewSet,
    WorkflowTransitionViewSet,
    ContentTemplateViewSet,
    ContentSnippetViewSet,
)
from .views.editor_views import EditorToolingViewSet
from .views.editor_tracking_views import EditorSessionViewSet, EditorProductivityMetricsViewSet
from .views.analytics_views import (
    EditorAnalyticsViewSet,
    BlogPostAnalyticsViewSet,
    ContentPerformanceMetricsViewSet,
)
from .views.content_audit_views import ContentAuditViewSet
from .views.enhanced_views import MediaBrowserViewSet
from .views.metrics_views import (
    WebsiteContentMetricsViewSet,
    WebsitePublishingTargetViewSet,
    CategoryPublishingTargetViewSet,
    ContentFreshnessReminderViewSet,
    ContentCalendarViewSet,
)
from .seo import robots_txt, sitemap_index, blog_sitemap
from .views import blog_redirect
from .views import preview_views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

# Swagger API Documentation Setup
schema_view = get_schema_view(
    openapi.Info(
        title="Blog Management API",
        default_version="v1",
        description="API documentation for the Blog Management system",
        terms_of_service="https://yourwebsite.com/terms/",
        contact=openapi.Contact(email="support@yourwebsite.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[AllowAny],
)

# Use DefaultRouter for CRUD-based ViewSets
router = DefaultRouter()
router.register(r'blogs', BlogPostViewSet, basename='blogs')
router.register(r'categories', BlogCategoryViewSet, basename='categories')
router.register(r'tags', BlogTagViewSet, basename='tags')
router.register(r'authors', AuthorProfileViewSet, basename='authors')
router.register(r'newsletters', NewsletterViewSet, basename='newsletters')
router.register(r'newsletter-subscribers', NewsletterSubscriberViewSet, basename='newsletter-subscribers')
router.register(r'newsletter-analytics', NewsletterAnalyticsViewSet, basename='newsletter-analytics')
router.register(r'blog-media', BlogMediaFileViewSet, basename='blog-media')
router.register(r'blog-videos', BlogVideoViewSet, basename='blog-videos')
router.register(r'blog-dark-mode-images', BlogDarkModeImageViewSet, basename='blog-dark-mode-images')
router.register(r"ab-tests", BlogABTestViewSet, basename="ab-tests")
router.register(r"clicks", BlogClickViewSet, basename="clicks")
router.register(r"conversions", BlogConversionViewSet, basename="conversions")
router.register(r"social-platforms", SocialPlatformViewSet, basename="social-platforms")
router.register(r"blog-shares", BlogShareViewSet, basename="blog-shares")

# Enhanced CMS routes
router.register(r"cta-blocks", CTABlockViewSet, basename="cta-block")
router.register(r"cta-placements", BlogCTAPlacementViewSet, basename="cta-placement")
router.register(r"content-block-templates", ContentBlockTemplateViewSet, basename="content-block-template")
router.register(r"content-blocks", BlogContentBlockViewSet, basename="content-block")
router.register(r"edit-history", BlogEditHistoryViewSet, basename="edit-history")
router.register(r"seo-metadata", BlogSEOMetadataViewSet, basename="seo-metadata")
router.register(r"faq-schemas", FAQSchemaViewSet, basename="faq-schema")
router.register(r"author-schemas", AuthorSchemaViewSet, basename="author-schema")

# PDF Sample routes
router.register(r"pdf-sample-sections", PDFSampleSectionViewSet, basename="pdf-sample-section")
router.register(r"pdf-samples", PDFSampleViewSet, basename="pdf-sample")
router.register(r"pdf-sample-downloads", PDFSampleDownloadViewSet, basename="pdf-sample-download")

# Draft & Editing routes
router.register(r"blog-revisions", BlogPostRevisionViewSet, basename="blog-revision")
router.register(r"blog-autosaves", BlogPostAutoSaveViewSet, basename="blog-autosave")
router.register(r"blog-edit-locks", BlogPostEditLockViewSet, basename="blog-edit-lock")
router.register(r"blog-previews", BlogPostPreviewViewSet, basename="blog-preview")

# Workflow & Templates routes
router.register(r"blog-workflows", BlogPostWorkflowViewSet, basename="blog-workflow")
router.register(r"review-comments", BlogPostReviewCommentViewSet, basename="review-comment")
router.register(r"workflow-transitions", WorkflowTransitionViewSet, basename="workflow-transition")
router.register(r"content-templates", ContentTemplateViewSet, basename="content-template")
router.register(r"content-snippets", ContentSnippetViewSet, basename="content-snippet")

# Editor Tooling routes
router.register(r"editor-tooling", EditorToolingViewSet, basename="editor-tooling")
router.register(r"editor-sessions", EditorSessionViewSet, basename="editor-session")
router.register(r"editor-productivity", EditorProductivityMetricsViewSet, basename="editor-productivity")

# Analytics routes
router.register(r"editor-analytics", EditorAnalyticsViewSet, basename="editor-analytics")
router.register(r"blog-analytics", BlogPostAnalyticsViewSet, basename="blog-analytics")
router.register(r"content-metrics", ContentPerformanceMetricsViewSet, basename="content-metrics")

# Content audit & media browser
router.register(r"content-audit", ContentAuditViewSet, basename="content-audit")
router.register(r"media-browser", MediaBrowserViewSet, basename="media-browser")
router.register(r"website-metrics", WebsiteContentMetricsViewSet, basename="website-metrics")
router.register(r"publishing-targets", WebsitePublishingTargetViewSet, basename="publishing-targets")
router.register(r"category-publishing-targets", CategoryPublishingTargetViewSet, basename="category-publishing-targets")
router.register(r"content-freshness-reminders", ContentFreshnessReminderViewSet, basename="content-freshness-reminders")
router.register(r"content-calendar", ContentCalendarViewSet, basename="content-calendar")

# Combine urlpatterns properly to prevent overwrites
urlpatterns = [
    # Swagger & API Docs
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

    # Include all router-based endpoints
    path('', include(router.urls)),

    # Admin notifications
    path("admin-notifications/", AdminNotificationsView.as_view(), name="admin-notifications"),

    # Soft Deletion & Restoration
    path('blogs/<int:blog_id>/restore/', RestoreSoftDeletedBlogView.as_view(), name='restore-blog'),
    path('blogs/<int:blog_id>/delete/', PermanentlyDeleteBlogView.as_view(), name='delete-blog'),

    # SEO: Robots.txt & Sitemaps (Supports Pagination)
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap_index, name="sitemap_index"),
    path("sitemap/<int:website_id>/<int:page>/", blog_sitemap, name="blog_sitemap"),

    # Redirect old blog URLs to new slugs
    path("blogs/old/<slug:old_slug>/", blog_redirect, name="blog-redirect"),
    
    # Preview endpoint (public)
    path("preview/<str:token>/", preview_views.preview_blog_post, name="blog-preview"),
]