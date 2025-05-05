from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DiscountViewSet, DiscountUsageViewSet,
    DiscountStackingRuleViewSet, SeasonalEventViewSet
)

router = DefaultRouter()

# Registering the viewsets
router.register(r'discounts', DiscountViewSet)
router.register(r'discount-usage', DiscountUsageViewSet)
router.register(r'discount-stacking-rules', DiscountStackingRuleViewSet)
router.register(r'seasonal-events', SeasonalEventViewSet)

urlpatterns = [
    # Include the router URLs for the discount and seasonal event endpoints
    path('api/', include(router.urls)),
]