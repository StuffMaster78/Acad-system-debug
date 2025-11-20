from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WebsiteViewSet, WebsiteActionLogViewSet, WebsiteStaticPageViewSet
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

# ✅ API Documentation (Swagger & ReDoc)
schema_view = get_schema_view(
    openapi.Info(
        title="Website Management API",
        default_version="v1",
        description="API for managing websites, SEO settings, soft deletion, and action logging.",
        terms_of_service="https://yourwebsite.com/terms/",
        contact=openapi.Contact(email="support@yourwebsite.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[AllowAny],
)

# ✅ Register Website Routes with DefaultRouter
router = DefaultRouter()
router.register(r'websites', WebsiteViewSet, basename='websites')
router.register(r'website-logs', WebsiteActionLogViewSet, basename='website-logs')
router.register(r"static-pages", WebsiteStaticPageViewSet, basename="static-page")

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

    # 📄 API Documentation (Swagger & ReDoc)
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]