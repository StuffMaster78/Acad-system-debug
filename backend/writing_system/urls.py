"""
URL configuration for writing_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
URL configuration for the writing_system project.

This `urlpatterns` list routes URLs to views for different parts of the project.
Includes API documentation, schema generation, and app-specific endpoints.
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)
from django.conf import settings
from django.conf.urls.static import static
from core.api_root import api_root
from core.views.health import health_check, health_ready, health_live

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls, name='admin'),
    path('sentry-debug/', trigger_error),

    # Health check endpoints (public, no authentication)
    path('health/', health_check, name='health-check'),
    path('health/ready/', health_ready, name='health-ready'),
    path('health/live/', health_live, name='health-live'),

    # API root endpoint (public)
    path('api/v1/', api_root, name='api-root'),

    # Endpoint proxy for masking (must be before other routes to catch masked endpoints)
    path('api/v1/proxy/', include('core.endpoint_proxy_urls')),

    # API schema and documentation
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/v1/docs/swagger/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='swagger-ui'),
    path('api/v1/docs/redoc/', SpectacularRedocView.as_view(url_name='api-schema'), name='redoc-ui'),

    # App-specific endpoints
    path('api/v1/orders/', include('orders.urls')),          # Orders app
    path('api/v1/discounts/', include('discounts.urls')),    # Discounts app
    path('api/v1/websites/', include('websites.urls')),      # Websites app
    path('api/v1/users/', include('users.urls')),            # Users app
    path('api/v1/client-management/', include('client_management.urls')),  # Client Management app
    path('api/v1/writer-management/', include(('writer_management.urls', 'writer_management'), namespace='writer_management')),  # Writer Management app
    path("api/v1/support-management/", include(('support_management.urls', 'support_management'), namespace='support_management')), # Support Management app
    # Backward-compatible alias some tests may use
    path("api/v1/support/", include(('support_management.urls', 'support_management'), namespace='support')),  # Alias with unique namespace
    path("api/v1/editor-management/", include("editor_management.urls")), # Editor Management app
    path("api/v1/admin-management/", include(('admin_management.urls', 'admin_management'), namespace='admin_management')), # Admin Management app
    path("api/v1/activity/", include('activity.urls')),  # Activity app URLs for general activity logs
    path("api/v1/superadmin-management/", include("superadmin_management.urls")), # Superadmin Management app

    path('api/v1/referrals/', include('referrals.urls')), # Referrals Management App
    path('api/v1/refunds/', include('refunds.urls')),
    path('api/v1/order-configs/', include('order_configs.urls')), 
    path('api/v1/pricing-configs/', include('pricing_configs.urls')),
    path('api/v1/loyalty-management/', include('loyalty_management.urls')),
    path('api/v1/loyalty_management/', include('loyalty_management.urls')),  # Alias for frontend compatibility
    path('api/v1/notifications/', include(('notifications_system.urls', 'notifications_system'), namespace='notifications')),
    path('api/v1/notifications_system/', include(('notifications_system.urls', 'notifications_system'), namespace='notifications_system')),  # Alias for frontend compatibility
    path('api/v1/order-communications/', include('communications.urls')),
    path('api/v1/order-files/', include('order_files.urls')),
    path('api/v1/order-payments/', include('order_payments_management.urls')),  # Order Payments Management
    path('api/v1/special-orders/', include('special_orders.urls')),
    path('api/v1/tickets/', include('tickets.urls')),
    path('api/v1/wallet/', include('wallet.urls')),
    path('api/v1/wallet/', include('client_wallet.urls')),  # Client Wallet Management
    path('api/v1/writer-wallet/', include('writer_wallet.urls')),  # Writer Wallet Management
    path('api/v1/writer-payments/', include('writer_payments_management.urls')),  # Writer Payments Management
    path('api/v1/mass-emails/', include('mass_emails.urls')),
    path('api/v1/blog_pages_management/', include('blog_pages_management.urls')),
    path('api/v1/service-pages/', include('service_pages_management.urls')),
    path('api/v1/fines/', include('fines.urls')),
    path('api/v1/reviews/', include('reviews_system.urls')),  # Reviews System
    path('api/v1/class-management/', include('class_management.urls')),  # Class Management (bundles & express classes)
    path('api/v1/media/', include('media_management.urls')),  # Media assets (images, videos, documents)
    path('api/v1/seo-pages/', include('seo_pages.urls')),  # SEO landing pages
    path('api/v1/public/', include('seo_pages.urls')),  # Public SEO pages endpoint
    path('api-auth/', include('rest_framework.urls')),  # Enables login/logout
    path('api/v1/analytics/', include('analytics.urls')),  # Analytics app
    path('api/v1/holidays/', include('holiday_management.urls')),  # Holiday Management app
    # path('api/v1/badge_management/', include('badge_management.urls')),  # Badges app

    # path('api/v1/admin/', include('notifications_system.admin_urls')), # Admin URLs for notifications

    path('api/v1/auth/', include('authentication.urls')),
    # Dropdown options endpoint (unified API for all dropdowns)
    path('api/v1/dropdown-options/', include('core.urls')),
    # Dashboard configuration endpoint
    path('api/v1/dashboard-config/', include('core.urls_dashboard')),
    # Configuration versioning
    path('api/v1/config-versioning/', include('core.urls_config_versioning')),
    # Note: Backward-compatible aliases removed to avoid URL namespace conflicts
    # Tests should use the /api/v1/ prefixed URLs instead
]

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)