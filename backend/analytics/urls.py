"""
Analytics URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClientAnalyticsViewSet,
    WriterAnalyticsViewSet,
    ClassAnalyticsViewSet,
    ContentEventViewSet,
)
from .chart_views import (
    RevenueTrendView,
    OrdersTrendView,
    ClientGrowthView,
    RevenueByWebsiteView,
    WriterEarningsTrendView,
    ClientSpendingTrendView,
)

router = DefaultRouter()
router.register(r'client', ClientAnalyticsViewSet, basename='client-analytics')
router.register(r'writer', WriterAnalyticsViewSet, basename='writer-analytics')
router.register(r'class', ClassAnalyticsViewSet, basename='class-analytics')
router.register(r'content-events', ContentEventViewSet, basename='content-events')

urlpatterns = [
    path('', include(router.urls)),
    # Chart-ready endpoints
    path('charts/revenue/', RevenueTrendView.as_view(), name='chart-revenue'),
    path('charts/orders/', OrdersTrendView.as_view(), name='chart-orders'),
    path('charts/clients/', ClientGrowthView.as_view(), name='chart-clients'),
    path('charts/revenue-by-website/', RevenueByWebsiteView.as_view(), name='chart-revenue-by-website'),
    path('charts/writer-earnings/', WriterEarningsTrendView.as_view(), name='chart-writer-earnings'),
    path('charts/client-spending/', ClientSpendingTrendView.as_view(), name='chart-client-spending'),
]

