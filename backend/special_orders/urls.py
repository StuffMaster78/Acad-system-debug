from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SpecialOrderViewSet,
    InstallmentPaymentViewSet,
    PredefinedSpecialOrderConfigViewSet,
    PredefinedSpecialOrderDurationViewSet,
    WriterBonusViewSet,
    EstimatedSpecialOrderSettingsViewSet
)

# Initialize the router for the viewsets
router = DefaultRouter()
router.register(
    r'special-orders',
    SpecialOrderViewSet
)
router.register(
    r'installment-payments',
    InstallmentPaymentViewSet
)
router.register(
    r'predefined-special-order-configs',
    PredefinedSpecialOrderConfigViewSet
)
router.register(
    r'predefined-special-order-durations',
    PredefinedSpecialOrderDurationViewSet
)
router.register(r'writer-bonuses', WriterBonusViewSet)
router.register(
    r'estimated-special-order-settings',
    EstimatedSpecialOrderSettingsViewSet,
    basename='estimatedspecialordersettings'
)

urlpatterns = [
    path('api/', include(router.urls)),  # API URLs for the viewsets
]