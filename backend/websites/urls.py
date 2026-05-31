from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.all_views import (
    WebsiteViewSet, WebsiteActionLogViewSet, WebsiteStaticPageViewSet,
    WebsiteIntegrationConfigViewSet
)
from .views.tenant_features import TenantFeatureToggleViewSet, TenantBrandingViewSet

# ✅ Register Website Routes with DefaultRouter
router = DefaultRouter()
router.register(r'websites', WebsiteViewSet, basename='websites')
router.register(r'website-logs', WebsiteActionLogViewSet, basename='website-logs')
router.register(r"static-pages", WebsiteStaticPageViewSet, basename="static-page")
router.register(r'branding', TenantBrandingViewSet, basename='tenant-branding')
router.register(r'feature-toggles', TenantFeatureToggleViewSet, basename='tenant-feature-toggle')
router.register(r'integrations', WebsiteIntegrationConfigViewSet, basename='website-integrations')

urlpatterns = [
    # 🌍 Website Management API
    path("", include(router.urls)),

    # ✅ SEO & Analytics Management (Admins & Superadmins Only)
    path("websites/<int:pk>/update_seo_settings/", WebsiteViewSet.as_view({"patch": "update_seo_settings"}), name="update-seo-settings"),

    # ✅ Soft Delete & Restore (Admins Only)
    path("websites/<int:pk>/soft_delete/", WebsiteViewSet.as_view({"post": "soft_delete"}), name="soft-delete"),
    path("websites/<int:pk>/restore/", WebsiteViewSet.as_view({"post": "restore"}), name="restore"),
    
    # 🌐 SEO & Analytics Management
    path("websites/<int:pk>/update_seo_settings/", WebsiteViewSet.as_view({"patch": "update_seo_settings"}), name="update-seo-settings"),
    path("websites/<int:pk>/soft_delete/", WebsiteViewSet.as_view({"post": "soft_delete"}), name="soft-delete"),
    path("websites/<int:pk>/restore/", WebsiteViewSet.as_view({"post": "restore"}), name="restore-website"),

    # ✅ Admin Action Logs API
    path("website-logs/", WebsiteActionLogViewSet.as_view({"get": "list"}), name="website-logs"),

    # API docs served by drf_spectacular at /api/v1/docs/ (project-level)
]