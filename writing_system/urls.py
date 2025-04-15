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
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.conf import settings
from django.conf.urls.static import static

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls, name='admin'),
    path('sentry-debug/', trigger_error),

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
    path('api/v1/writer-management/', include('writer_management.urls')),  # Writer Management app
    path("api/v1/support-management/", include("support_management.urls")), # Support Management app
    path("api/v1/editor-management/", include("editor_management.urls")), # Editor Management app
    path("api/v1/admin-management/", include("admin_management.urls")), # Admin Management app
    path("api/v1/superadmin-management/", include("superadmin_management.urls")), # Superadmin Management app

    path('api/v1/referrals/', include('referrals.urls')), # Referrals Management App
    path('api/v1/order-configs/', include('order_configs.urls')), 
    path('api/v1/pricing-configs/', include('pricing_configs.urls')),
    path('api/v1/loyalty-management/', include('loyalty_management.urls')),
    path('api/v1/notifications/', include('notifications_system.urls')),
    path('api/v1/order-communications/', include('order_communications.urls')),
    path('api/v1/order-files/', include('order_files.urls')),
    path('api/v1/referrals/', include('referrals.urls')),
    path('api/v1/special-orders/', include('special_orders.urls')),
    path('api/v1/tickets/', include('tickets.urls')),
    path('api/v1/wallet/', include('wallet.urls')),
    path('api/v1/blog_pages_management/', include('blog_pages_management.urls')),
    path('api/v1/', include('service_pages_management.urls')),
    path('api-auth/', include('rest_framework.urls')),  # Enables login/logout

    path('/api/v1/auth/', include('authentication.urls')),
]

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)