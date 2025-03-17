from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BlogPostViewSet, BlogCategoryViewSet, BlogTagViewSet,
    AuthorProfileViewSet, BlogClickView, BlogConversionView,
    RestoreSoftDeletedBlogView, PermanentlyDeleteBlogView,
    AdminNotificationsView, NewsletterSubscriberViewSet,
    NewsletterViewSet, NewsletterAnalyticsViewSet,
    BlogMediaFileViewSet, BlogVideoViewSet,
    BlogDarkModeImageViewSet, BlogABTestViewSet, 
    BlogConversionViewSet, BlogClickViewSet,
    SocialPlatformViewSet, BlogShareViewSet
)
from .seo import robots_txt, sitemap_index, blog_sitemap

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

urlpatterns = [
    path('', include(router.urls)),  # Includes all router-based endpoints

    # ✅ Admin notifications (removed duplicate entry)
    path("admin-notifications/", AdminNotificationsView.as_view(), name="admin-notifications"),

    # ✅ Blog Engagement Tracking (Clicks & Conversions)
    path('blogs/<int:blog_id>/click/', BlogClickView.as_view(), name='blog-click'),
    path('blogs/<int:blog_id>/conversion/', BlogConversionView.as_view(), name='blog-conversion'),

    # ✅ Soft Deletion & Restoration
    path('blogs/<int:blog_id>/restore/', RestoreSoftDeletedBlogView.as_view(), name='restore-blog'),
    path('blogs/<int:blog_id>/delete/', PermanentlyDeleteBlogView.as_view(), name='delete-blog'),

    # ✅ Related Blogs & Broken Links Detection
    path('blogs/<int:pk>/related/', BlogPostViewSet.as_view({'get': 'related_posts'}), name='related-blogs'),
    path('blogs/<int:pk>/detect_broken_links/', BlogPostViewSet.as_view({'get': 'detect_broken_links'}), name='detect-broken-links'),
    path('blogs/<int:pk>/fix_broken_links/', BlogPostViewSet.as_view({'post': 'fix_broken_links'}), name='fix-broken-links'),

    # ✅ Blog Share URLs & Increment Share Count
    path("blog-shares/generate-url/", BlogShareViewSet.as_view({"post": "generate_share_url"}), name="generate-share-url"),
    path("blog-shares/increment-share/", BlogShareViewSet.as_view({"post": "increment_share"}), name="increment-share"),

    # ✅ Toggle Social Platform Status
    path(
        "social-platforms/<int:pk>/toggle-status/",
        SocialPlatformViewSet.as_view({"patch": "toggle_platform_status"}),
        name="toggle-platform-status"
    ),

    # ✅ SEO: Robots.txt & Sitemaps (Supports Pagination)
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap_index, name="sitemap_index"),
    path("sitemap/<int:website_id>/<int:page>/", blog_sitemap, name="blog_sitemap"),
]