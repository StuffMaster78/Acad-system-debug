from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RefundViewSet,
    RefundLogViewSet,
    RefundReceiptViewSet
)

router = DefaultRouter()
router.register(
    r'refunds', RefundViewSet,
    basename='refund'
)
router.register(
    r'refund-logs', RefundLogViewSet,
    basename='refund-log'
)
router.register(
    r'refund-receipts', RefundReceiptViewSet,
    basename='refund-receipt'
)

urlpatterns = [
    path('', include(router.urls)),
]
