# writer_management/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from writer_management.views.badge_analytics import BadgeAnalyticsViewSet, BadgeAchievementViewSet, BadgePerformanceViewSet
from writer_management.views import (
    WriterProfileViewSet,
    WriterConfigViewSet,
    WriterOrderRequestViewSet,
    WriterOrderTakeViewSet,
    WriterSupportTicketViewSet,
    WriterSuspensionViewSet,
    WriterDeadlineExtensionRequestViewSet,
)

# Namespace for writer_management URLs
app_name = "writer_management"

# Create router for badge analytics
router = DefaultRouter()
router.register(r'badge-analytics', BadgeAnalyticsViewSet, basename='badge-analytics')
router.register(r'badge-achievements', BadgeAchievementViewSet, basename='badge-achievements')
router.register(r'badge-performance', BadgePerformanceViewSet, basename='badge-performance')
router.register(r'writers', WriterProfileViewSet, basename='writers')
router.register(r'writer-configs', WriterConfigViewSet, basename='writer-configs')
router.register(r'writer-order-requests', WriterOrderRequestViewSet, basename='writer-order-requests')
router.register(r'writer-order-takes', WriterOrderTakeViewSet, basename='writer-order-takes')
router.register(r'writer-support-tickets', WriterSupportTicketViewSet, basename='writer-support-tickets')
router.register(r'writer-suspensions', WriterSuspensionViewSet, basename='writer-suspensions')
router.register(r'writer-deadline-extension-requests', WriterDeadlineExtensionRequestViewSet, basename='writer-deadline-extension-requests')

urlpatterns = [
    path('', include(router.urls)),
]