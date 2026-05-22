"""
Project URL configuration.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from core.api_root import api_root
from core.views.health import health_check, health_live, health_ready
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from cms_core.api import api_router

support_urls = ("support_management.urls", "support_management")
writer_urls = ("writer_management.urls", "writer_management")
admin_urls = ("admin_management.urls", "admin_management")
notification_urls = ("notifications_system.urls", "notifications_system")


urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("health/", health_check, name="health-check"),
    path("health/ready/", health_ready, name="health-ready"),
    path("health/live/", health_live, name="health-live"),
    path("api/v1/", api_root, name="api-root"),
    path("api/v1/proxy/", include("core.endpoint_proxy_urls")),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/v1/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="swagger-ui",
    ),
    path(
        "api/v1/docs/redoc/",
        SpectacularRedocView.as_view(url_name="api-schema"),
        name="redoc-ui",
    ),
    path("api/v1/orders/", include("orders.urls")),
    path("api/v1/discounts/", include("discounts.urls")),
    path("api/v1/websites/", include("websites.urls")),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/client-management/", include("client_management.urls")),
    path(
        "api/v1/writer-management/",
        include(writer_urls, namespace="writer_management"),
    ),
    path(
        "api/v1/support-management/",
        include(support_urls, namespace="support_management"),
    ),
    path(
        "api/v1/support/",
        include(support_urls, namespace="support"),
    ),
    path("api/v1/editor-management/", include("editor_management.urls")),
    path(
        "api/v1/admin-management/",
        include(admin_urls, namespace="admin_management"),
    ),
    path("api/v1/activity/", include("activity.urls")),
    path(
        "api/v1/superadmin-management/",
        include("superadmin_management.urls"),
    ),
    path("api/v1/referrals/", include("referrals.urls")),
    path("api/v1/refunds/", include("refunds.urls")),
    path("api/v1/order-configs/", include("order_configs.urls")),
    path("api/v1/pricing/", include("order_pricing_core.urls")),
    path("api/v1/loyalty-management/", include("loyalty_management.urls")),
    path(
        "api/v1/notifications/",
        include(notification_urls, namespace="notifications"),
    ),
    path("api/orders/", include("orders.api.urls")),
    path("api/v1/files/", include("files_management.urls")),
    path("api/v1/tickets/", include("tickets.urls")),
    path(
        "api/v1/writer-compensation/",
        include("writer_compensation.urls"),
    ),
    path("api/v1/mass-emails/", include("mass_emails.urls")),
    path(
        "api/v1/blog_pages_management/",
        include("blog_pages_management.urls"),
    ),
    path("api/v1/service-pages/", include("service_pages_management.urls")),
    path("api/v1/fines/", include("fines.urls")),
    path("api/v1/reviews/", include("reviews_system.urls")),
    path("api/v1/class-management/", include("class_management.urls")),
    path("api/v1/special-orders/", include("special_orders.urls")),
    path("api/v1/media/", include("media_management.urls")),
    path("api/v1/seo-pages/", include("seo_pages.urls")),
    path("api/v1/public/", include("seo_pages.urls")),
    path("api/v1/announcements/", include("announcements.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("api/v1/analytics/", include("analytics.urls")),
    path("api/v1/holidays/", include("holiday_management.urls")),
    path(
        "api/v1/wallets/",
        include("wallets.urls", namespace="wallets"),
    ),
    path("api/v1/ledger/", include("ledger.urls", namespace="ledger")),
    path("api/v1/auth/", include("authentication.urls")),
    path("api/v1/dropdown-options/", include("core.urls")),
    path("api/v1/dashboard-config/", include("core.urls_dashboard")),
    path(
        "api/v1/config-versioning/",
        include("core.urls_config_versioning"),
    ),
    path("api/v1/communications/", include("communications.urls")),
    path("api/v1/tips/", include("tips.urls")),
    path("cms-admin/", include(wagtailadmin_urls)),    # Wagtail admin
    path("api/v2/", api_router.urls),                  # Wagtail headless API
    path("", include(wagtail_urls)),                   # Wagtail page serving (keep last)
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )
