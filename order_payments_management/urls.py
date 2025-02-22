from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderPaymentViewSet, RefundViewSet, PaymentNotificationViewSet,
    PaymentLogViewSet, PaymentDisputeViewSet, DiscountUsageViewSet,
    SplitPaymentViewSet, AdminLogViewSet, PaymentReminderSettingsViewSet,
    TransactionViewSet
)

# Create a router for RESTful ViewSets
router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transactions')
router.register(r'payment-notifications', PaymentNotificationViewSet, basename='payment-notifications')
router.register(r'payment-logs', PaymentLogViewSet, basename='payment-logs')
router.register(r'discount-usage', DiscountUsageViewSet, basename='discount-usage')
router.register(r'admin-logs', AdminLogViewSet, basename='admin-logs')
router.register(r'payment-reminder-settings', PaymentReminderSettingsViewSet, basename='payment-reminder-settings')

# Include router-generated URLs
urlpatterns = [
    path('api/', include(router.urls)),
]