# writer_management/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from writer_management.views.badge_analytics import BadgeAnalyticsViewSet, BadgeAchievementViewSet, BadgePerformanceViewSet
from writer_management.views import (
    WriterProfileViewSet,
    WriterConfigViewSet,
    WriterLevelConfigViewSet,
    WriterOrderRequestViewSet,
    WriterOrderTakeViewSet,
    WriterSupportTicketViewSet,
    WriterSuspensionViewSet,
    WriterDeadlineExtensionRequestViewSet,
)
# Import performance views from views package
from writer_management.views import WriterPerformanceSnapshotViewSet, WriterPerformanceDashboardView
from writer_management.views_dashboard import WriterDashboardViewSet
# Import Tip views from views.tips module
from writer_management.views.tips import TipViewSet, TipListView

# app_name removed to allow explicit namespaces in main urls.py
# app_name = "writer_management"

# Create router for badge analytics
router = DefaultRouter()
router.register(r'badge-analytics', BadgeAnalyticsViewSet, basename='badge-analytics')
router.register(r'badge-achievements', BadgeAchievementViewSet, basename='badge-achievements')
router.register(r'badge-performance', BadgePerformanceViewSet, basename='badge-performance')
router.register(r'writers', WriterProfileViewSet, basename='writers')
router.register(r'writer-configs', WriterConfigViewSet, basename='writer-configs')
router.register(r'writer-level-configs', WriterLevelConfigViewSet, basename='writer-level-configs')
router.register(r'writer-order-requests', WriterOrderRequestViewSet, basename='writer-order-requests')
router.register(r'writer-order-takes', WriterOrderTakeViewSet, basename='writer-order-takes')
router.register(r'writer-support-tickets', WriterSupportTicketViewSet, basename='writer-support-tickets')
router.register(r'writer-suspensions', WriterSuspensionViewSet, basename='writer-suspensions')
router.register(r'writer-deadline-extension-requests', WriterDeadlineExtensionRequestViewSet, basename='writer-deadline-extension-requests')
router.register(r'writer-performance-snapshots', WriterPerformanceSnapshotViewSet, basename='writer-performance-snapshots')
router.register(r'dashboard', WriterDashboardViewSet, basename='writer-dashboard')
router.register(r'tips', TipViewSet, basename='tips')

urlpatterns = [
    path('', include(router.urls)),
    path('writer-performance-dashboard/<int:pk>/', WriterPerformanceDashboardView.as_view(), name='writer-performance-dashboard'),
    # Legacy endpoint for backward compatibility
    path('tips/list/', TipListView.as_view(), name='tip-list'),
]