from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DiscountViewSet, DiscountUsageViewSet,
    DiscountStackingRuleViewSet, PromotionalCampaignViewSet,
    DiscountAnalyticsView, SeasonalEventViewSet
)

router = DefaultRouter()

# Registering the viewsets
router.register(r'discounts', DiscountViewSet, basename='discounts')
router.register(r'discount-usage', DiscountUsageViewSet, basename='discount-usage')
router.register(r'discount-stacking-rules', DiscountStackingRuleViewSet, basename='discount-stacking-rules')
router.register(r'promotional-campaigns', PromotionalCampaignViewSet, basename='promotional-campaigns')
router.register(r'seasonal-events', SeasonalEventViewSet, basename='seasonal-events')

urlpatterns = [
    # Expose endpoints without extra prefix; parent includes may add /api/
    path('', include(router.urls)),
    path(
        "discounts/analytics/",
        DiscountAnalyticsView.as_view(),
        name="discount-analytics"
    ),
]