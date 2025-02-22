from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from django.db.models.functions import Coalesce
from .models import (
    OrderPayment, Refund, PaymentNotification, PaymentLog,
    PaymentDispute, DiscountUsage, SplitPayment, AdminLog,
    PaymentReminderSettings
)
from .serializers import (
    TransactionSerializer, PaymentNotificationSerializer,
    PaymentLogSerializer, PaymentDisputeSerializer, DiscountUsageSerializer,
    AdminLogSerializer, PaymentReminderSettingsSerializer
)
from rest_framework.pagination import PageNumberPagination


class TransactionPagination(PageNumberPagination):
    """
    Custom pagination for transactions.
    Allows adjusting page size via query params.
    """
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only API for fetching all transactions (Payments, Refunds, Split Payments).
    Clients see only their transactions, while admins see all.
    Supports filtering by transaction type.
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TransactionPagination
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        """
        - Clients: See only their own transactions.
        - Admins: See all transactions.
        - Filters: Supports `?transaction_type=payment/refund/split_payment`
        """
        user = self.request.user
        transaction_type = self.request.query_params.get("transaction_type", None)

        # Base query logic
        if user.is_staff:
            transactions = list(OrderPayment.objects.all()) + \
                           list(Refund.objects.all()) + \
                           list(SplitPayment.objects.all())
        else:
            transactions = list(OrderPayment.objects.filter(client=user)) + \
                           list(Refund.objects.filter(client=user)) + \
                           list(SplitPayment.objects.filter(payment__client=user))

        # Filter by transaction type
        if transaction_type:
            if transaction_type == "payment":
                transactions = [t for t in transactions if isinstance(t, OrderPayment)]
            elif transaction_type == "refund":
                transactions = [t for t in transactions if isinstance(t, Refund)]
            elif transaction_type == "split_payment":
                transactions = [t for t in transactions if isinstance(t, SplitPayment)]

        # Sort transactions by date (latest first)
        transactions.sort(key=lambda x: getattr(x, "date_processed", timezone.now()), reverse=True)

        return transactions


class PaymentNotificationViewSet(viewsets.ReadOnlyModelViewSet, mixins.UpdateModelMixin):
    """
    Handles payment notifications.
    Clients can list their notifications and mark them as read.
    """
    queryset = PaymentNotification.objects.select_related("user", "payment")
    serializer_class = PaymentNotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["user", "is_read"]

    def get_queryset(self):
        """Filters notifications for the logged-in user."""
        return self.queryset.filter(user=self.request.user)


class PaymentLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides a read-only API for payment logs.
    Useful for auditing purposes.
    """
    queryset = PaymentLog.objects.select_related("payment")
    serializer_class = PaymentLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["payment"]


class PaymentDisputeViewSet(viewsets.ModelViewSet):
    """
    Allows clients to dispute a payment.
    Clients can create disputes, and admins can resolve them.
    """
    queryset = PaymentDispute.objects.select_related("client", "payment")
    serializer_class = PaymentDisputeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["client", "status"]

    def perform_create(self, serializer):
        """Ensures the dispute is linked to the requesting user."""
        serializer.save(client=self.request.user)


class DiscountUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides a read-only API for tracking discount usage.
    Clients can view their applied discounts.
    """
    queryset = DiscountUsage.objects.select_related("discount", "user", "order", "special_order")
    serializer_class = DiscountUsageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["user", "discount"]


class AdminLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides a read-only API for admin logs.
    Useful for tracking admin actions related to payments.
    """
    queryset = AdminLog.objects.select_related("admin")
    serializer_class = AdminLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["admin", "action", "timestamp"]


class PaymentReminderSettingsViewSet(viewsets.ModelViewSet):
    """
    Allows admins to update payment reminder settings.
    """
    queryset = PaymentReminderSettings.objects.all()
    serializer_class = PaymentReminderSettingsSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """Ensures only one global settings entry is retrieved."""
        return PaymentReminderSettings.objects.all()[:1]