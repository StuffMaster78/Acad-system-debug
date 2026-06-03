from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cms_intelligence.views import (
    AnswersSearchView,
    DashboardView,
    FreshnessAlertViewSet,
    PerformanceSnapshotViewSet,
    PersonalizationRuleViewSet,
    SearchLogAnalyticsView,
    SyncStatusView,
)

router = DefaultRouter()
router.register("performance",     PerformanceSnapshotViewSet,  basename="performance")
router.register("freshness",       FreshnessAlertViewSet,        basename="freshness")
router.register("dashboard",       DashboardView,                basename="dashboard")
router.register("sync-status",     SyncStatusView,               basename="sync-status")
router.register("answers",         AnswersSearchView,            basename="answers")
router.register("search-log",      SearchLogAnalyticsView,       basename="search-log")
router.register("personalization", PersonalizationRuleViewSet,   basename="personalization")

app_name = "cms_intelligence"

urlpatterns = [
    path("", include(router.urls)),
]
