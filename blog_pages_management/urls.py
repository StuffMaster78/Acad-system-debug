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
from .seo import robots_txt, sitemap_index, blog_sitemap
from .views import blog_redirect
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

# ✅ Swagger API Documentation Setup
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

# ✅ Use DefaultRouter for CRUD-based ViewSets
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

# ✅ Combine urlpatterns properly to prevent overwrites
urlpatterns = [
    # ✅ Swagger & API Docs
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

    # ✅ Include all router-based endpoints
    path('', include(router.urls)),

    # ✅ Admin notifications
    path("admin-notifications/", AdminNotificationsView.as_view(), name="admin-notifications"),

    # ✅ Soft Deletion & Restoration
    path('blogs/<int:blog_id>/restore/', RestoreSoftDeletedBlogView.as_view(), name='restore-blog'),
    path('blogs/<int:blog_id>/delete/', PermanentlyDeleteBlogView.as_view(), name='delete-blog'),

    # ✅ SEO: Robots.txt & Sitemaps (Supports Pagination)
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap_index, name="sitemap_index"),
    path("sitemap/<int:website_id>/<int:page>/", blog_sitemap, name="blog_sitemap"),

    # ✅ Redirect old blog URLs to new slugs
    path("blogs/old/<slug:old_slug>/", blog_redirect, name="blog-redirect"),
]