from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView  # type: ignore
from .swagger import SecureSwaggerView, SecureRedocView
from .views import ServicePageViewSet
from .views.pdf_views import (
    ServicePagePDFSampleSectionViewSet,
    ServicePagePDFSampleViewSet,
)
from .views.metrics_views import ServiceWebsiteContentMetricsViewSet

router = DefaultRouter()
router.register(r"service-pages", ServicePageViewSet, basename="service-pages")
router.register(
    r"service-page-pdf-sample-sections",
    ServicePagePDFSampleSectionViewSet,
    basename="service-page-pdf-sample-section",
)
router.register(
    r"service-page-pdf-samples",
    ServicePagePDFSampleViewSet,
    basename="service-page-pdf-sample",
)
router.register(
    r"service-website-metrics",
    ServiceWebsiteContentMetricsViewSet,
    basename="service-website-metrics",
)

urlpatterns = [
    # Core API
    path("", include(router.urls)),
    # Schema endpoint
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    # Secure Swagger UI
    path(
        "docs/swagger/",
        SecureSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Secure Redoc UI
    path(
        "docs/redoc/",
        SecureRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]