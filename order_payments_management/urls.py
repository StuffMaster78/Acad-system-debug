from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import viewsets from views.py (the file, not the package)
import sys
import importlib.util
import os

# Import from views.py file directly
views_py_path = os.path.join(os.path.dirname(__file__), 'views.py')
spec = importlib.util.spec_from_file_location("order_payments_management.views_file", views_py_path)
views_file = importlib.util.module_from_spec(spec)
spec.loader.exec_module(views_file)

# Import InvoiceViewSet from views package
from .views.invoice_views import InvoiceViewSet

# Get viewsets from views.py
OrderPaymentViewSet = views_file.OrderPaymentViewSet
PaymentNotificationViewSet = views_file.PaymentNotificationViewSet
PaymentLogViewSet = views_file.PaymentLogViewSet
PaymentDisputeViewSet = views_file.PaymentDisputeViewSet
DiscountUsageViewSet = views_file.DiscountUsageViewSet
AdminLogViewSet = views_file.AdminLogViewSet
PaymentReminderSettingsViewSet = views_file.PaymentReminderSettingsViewSet
TransactionViewSet = views_file.TransactionViewSet
PaymentViewSet = views_file.PaymentViewSet
PaymentReminderConfigViewSet = views_file.PaymentReminderConfigViewSet
PaymentReminderDeletionMessageViewSet = views_file.PaymentReminderDeletionMessageViewSet
PaymentReminderSentViewSet = views_file.PaymentReminderSentViewSet

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
router.register(r'payment-reminder-configs', PaymentReminderConfigViewSet, basename='payment-reminder-configs')
router.register(r'payment-deletion-messages', PaymentReminderDeletionMessageViewSet, basename='payment-deletion-messages')
router.register(r'payment-reminders-sent', PaymentReminderSentViewSet, basename='payment-reminders-sent')
router.register(r'payments', PaymentViewSet, basename='payments')
router.register(r'invoices', InvoiceViewSet, basename='invoices')

# Include router-generated URLs
urlpatterns = [
    path('', include(router.urls)),
]
