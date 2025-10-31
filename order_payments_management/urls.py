from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderPaymentViewSet, PaymentNotificationViewSet,
    PaymentLogViewSet, PaymentDisputeViewSet, DiscountUsageViewSet,
    AdminLogViewSet, PaymentReminderSettingsViewSet, TransactionViewSet,
    RefundViewSet, PaymentViewSet
)

# Create a router for RESTful ViewSets
router = DefaultRouter()
router.register(r'order-payments', OrderPaymentViewSet, basename='order-payments')
router.register(r'transactions', TransactionViewSet, basename='transactions')
router.register(r'payment-notifications', PaymentNotificationViewSet, basename='payment-notifications')
router.register(r'payment-logs', PaymentLogViewSet, basename='payment-logs')
router.register(r'payment-disputes', PaymentDisputeViewSet, basename='payment-disputes')
router.register(r'discount-usage', DiscountUsageViewSet, basename='discount-usage')
router.register(r'admin-logs', AdminLogViewSet, basename='admin-logs')
router.register(r'payment-reminder-settings', PaymentReminderSettingsViewSet, basename='payment-reminder-settings')
router.register(r'refunds', RefundViewSet, basename='refunds')
router.register(r'payments', PaymentViewSet)

# Include router-generated URLs
urlpatterns = [
    path('', include(router.urls)),
]
