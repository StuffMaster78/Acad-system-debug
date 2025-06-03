from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DiscountViewSet, DiscountUsageViewSet,
    DiscountStackingRuleViewSet, PromotionalCamoaignViewSet,
    DiscountAnalyticsView
)

router = DefaultRouter()

# Registering the viewsets
router.register(r'discounts', DiscountViewSet, basename='discounts')
router.register(r'discount-usage', DiscountUsageViewSet, basename='discount-usage')
router.register(r'discount-stacking-rules', DiscountStackingRuleViewSet, basename='discount-stacking-rules')
router.register(r'promotional-campaigns', PromotionalCamoaignViewSet, basename='promotional-campaigns')

urlpatterns = [
    # Include the router URLs for the discount and promotional campaign endpoints
    path('api/', include(router.urls)),
    path(
        "api/discounts/analytics/",
        DiscountAnalyticsView.as_view(),
        name="discount-analytics"
    ),
]