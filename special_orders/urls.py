from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SpecialOrderViewSet,
    InstallmentPaymentViewSet,
    PredefinedSpecialOrderConfigViewSet,
    PredefinedSpecialOrderDurationViewSet,
    WriterBonusViewSet
)

router = DefaultRouter()
router.register(r'special-orders', SpecialOrderViewSet, basename='special-order')
router.register(r'installments', InstallmentPaymentViewSet, basename='installment')
router.register(r'predefined-orders', PredefinedSpecialOrderConfigViewSet, basename='predefined-order')
router.register(r'predefined-durations', PredefinedSpecialOrderDurationViewSet, basename='predefined-duration')
router.register(r'writer-bonuses', WriterBonusViewSet, basename='writer-bonus')

urlpatterns = [
    path('', include(router.urls)),
]