from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WriterWalletViewSet, WalletTransactionViewSet, 
    WriterPaymentBatchViewSet, PaymentScheduleViewSet,
    ScheduledWriterPaymentViewSet, PaymentOrderRecordViewSet, 
    WriterPaymentViewSet, AdminPaymentAdjustmentViewSet,
    PaymentConfirmationViewSet
)

router = DefaultRouter()
router.register("writer-wallets", WriterWalletViewSet)
router.register("wallet-transactions", WalletTransactionViewSet)
router.register("payment-batches", WriterPaymentBatchViewSet)
router.register("payment-schedules", PaymentScheduleViewSet)
router.register("scheduled-payments", ScheduledWriterPaymentViewSet, basename="scheduled-payments")
router.register("payment-order-records", PaymentOrderRecordViewSet)
router.register("writer-payments", WriterPaymentViewSet)
router.register("payment-adjustments", AdminPaymentAdjustmentViewSet)
router.register("payment-confirmations", PaymentConfirmationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]