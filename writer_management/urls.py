# writer_management/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from writer_management.views.badge_analytics import BadgeAnalyticsViewSet, BadgeAchievementViewSet, BadgePerformanceViewSet

# Namespace for writer_management URLs
app_name = "writer_management"

# Create router for badge analytics
router = DefaultRouter()
router.register(r'badge-analytics', BadgeAnalyticsViewSet, basename='badge-analytics')
router.register(r'badge-achievements', BadgeAchievementViewSet, basename='badge-achievements')
router.register(r'badge-performance', BadgePerformanceViewSet, basename='badge-performance')

urlpatterns = [
    path('', include(router.urls)),
]