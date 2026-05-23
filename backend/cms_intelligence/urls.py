from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cms_intelligence.views import (
    DashboardView,
    FreshnessAlertViewSet,
    PerformanceSnapshotViewSet,
)

router = DefaultRouter()
router.register("performance", PerformanceSnapshotViewSet, basename="performance")
router.register("freshness", FreshnessAlertViewSet, basename="freshness")
router.register("dashboard", DashboardView, basename="dashboard")

app_name = "cms_intelligence"

urlpatterns = [
    path("", include(router.urls)),
]
