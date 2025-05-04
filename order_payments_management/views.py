from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend # type: ignore
from django.db.models import Q
from django.utils import timezone
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
import logging
from rest_framework.decorators import action
from django.db import transaction
from django.db.models import Sum 
from orders.models import Order
from discounts.models import Discount

from .models import (
    OrderPayment, Refund,
    PaymentNotification, PaymentLog,
    PaymentDispute, DiscountUsage,
    SplitPayment, AdminLog,
    PaymentReminderSettings, RequestPayment
)
from .serializers import (
    TransactionSerializer, PaymentNotificationSerializer,
    PaymentLogSerializer, PaymentDisputeSerializer,
    DiscountUsageSerializer, AdminLogSerializer,
    PaymentReminderSettingsSerializer, RefundSerializer,
    RequestPaymentSerializer
)
from .permissions import IsSuperadminOrAdmin

logger = logging.getLogger(__name__)

class OrderPaymentViewSet(viewsets.ModelViewSet):
    """
    Viewset for handling order payments, including refunds.
    """
    queryset = OrderPayment.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]
    http_method_names = ["get", "post", "patch", "delete"]  # Limit methods if needed

    def refund_payment(self, request, pk=None):
        """
        Admin/Superadmin can refund a completed payment.
        """
        payment = get_object_or_404(OrderPayment, pk=pk)

        if payment.status != "completed":
            return Response(
                {"error": "Only completed payments can be refunded."},
                status=status.HTTP_400_BAD_REQUEST
            )

        reason = request.data.get("reason", "No reason provided")

        try:
            payment.refund(reason)
            return Response(
                {"message": "Payment refunded successfully."},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    # @action(detail=True, methods=["post"])
    # def retry_payment(self, request, pk=None):
    #     """
    #     Allows retrying a failed payment.
    #     """
    #     payment = get_object_or_404(OrderPayment, pk=pk)

    #     if payment.status != "failed":
    #         return Response({"error": "Only failed payments can be retried."}, 
    #                         status=status.HTTP_400_BAD_REQUEST)

    #     try:
    #         payment.retry()  # Assuming your model has a retry method
    #         return Response({"message": "Payment retry initiated."}, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=["post"])
    def cancel_payment(self, request, pk=None):
        """
        Allows an admin to cancel a pending payment.
        """
        payment = get_object_or_404(OrderPayment, pk=pk)

        if payment.status not in ["pending", "failed"]:
            return Response({"error": "Only pending or failed payments can be canceled."},
                            status=status.HTTP_400_BAD_REQUEST)

        payment.status = "canceled"
        payment.save()

        return Response({"message": "Payment canceled successfully."}, status=status.HTTP_200_OK)


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

        # Optimize QuerySet filtering
        if user.is_staff:
            queryset = OrderPayment.objects.all().union(
                Refund.objects.all(),
                SplitPayment.objects.all()
            )
        else:
            queryset = OrderPayment.objects.filter(client=user).union(
                Refund.objects.filter(client=user),
                SplitPayment.objects.filter(payment__client=user)
            )

        # Filter by transaction type
        if transaction_type:
            model_mapping = {
                "payment": OrderPayment,
                "refund": Refund,
                "split_payment": SplitPayment
            }
            model = model_mapping.get(transaction_type)
            if model:
                queryset = queryset.filter(id__in=model.objects.values_list("id", flat=True))

        return queryset.order_by("-date_processed")


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

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def escalate(self, request, pk=None):
        """
        Escalates a dispute for further review.
        """
        dispute = get_object_or_404(PaymentDispute, pk=pk)

        if dispute.status not in ["pending", "under_review"]:
            return Response({"error": "Only pending or under review disputes can be escalated."},
                            status=status.HTTP_400_BAD_REQUEST)

        dispute.status = "escalated"
        dispute.save()

        return Response({"message": "Dispute escalated successfully."}, status=status.HTTP_200_OK)


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
    

class RefundViewSet(viewsets.ModelViewSet):
    """
    RESTful API for handling refunds.
    - Admins can issue full or partial refunds.
    - Clients can view their own refunds.
    """
    queryset = Refund.objects.select_related("payment", "client", "processed_by").all()
    serializer_class = RefundSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["client", "status"]

    def get_permissions(self):
        """Ensure only admins can create or approve refunds."""
        if self.action in ["create", "partial_update", "update", "destroy"]:
            return [IsSuperadminOrAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        """Clients see only their refunds; Admins see all refunds."""
        user = self.request.user
        return self.queryset if user.is_staff else self.queryset.filter(client=user)

    def perform_create(self, serializer):
        """Handles refund logic with transaction safety and business rules."""
        user = self.request.user
        request = self.request  # Get request from self.request
        
        if not user.is_staff:
            return Response({"error": "Only admins can issue refunds."}, status=status.HTTP_403_FORBIDDEN)

        payment_id = request.data.get("payment_id")
        refund_amount = float(request.data.get("amount", 0))

        with transaction.atomic():
            payment = get_object_or_404(OrderPayment.objects.select_for_update(), transaction_id=payment_id)

            # Validate refund conditions
            total_refunded = Refund.objects.filter(payment=payment).aggregate(total=Sum("amount"))["total"] or 0
            remaining_refundable = payment.amount_paid - total_refunded

            if remaining_refundable <= 0:
                return Response({"error": "This payment has already been fully refunded."}, status=status.HTTP_400_BAD_REQUEST)

            if payment.status != "completed":
                return Response({"error": "Only completed payments can be refunded."}, status=status.HTTP_400_BAD_REQUEST)

            if payment.is_disputed:
                return Response({"error": "Refund cannot be issued while payment is under dispute."}, status=status.HTTP_400_BAD_REQUEST)

            if refund_amount > remaining_refundable:
                return Response({"error": "Refund amount exceeds the remaining refundable amount."}, status=status.HTTP_400_BAD_REQUEST)

            # Determine refund destination (original method or wallet)
            refund_destination = "wallet" if payment.payment_method == "wallet" else "original"

            # Create and process refund
            refund = serializer.save(
                payment=payment,
                client=payment.client,
                processed_by=user,
                status="processed",
                processed_at=timezone.now(),
                amount=refund_amount
            )

            # Notify client
            PaymentNotification.objects.create(
                user=payment.client,
                message=f"Your refund of {refund.amount} has been processed to your {refund_destination}."
            )

            return Response({"message": "Refund processed successfully."}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """Disallow updating refunds manually to maintain integrity."""
        return Response({"error": "Refunds cannot be modified once processed."}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        """Disallow refund deletion for audit tracking."""
        return Response({"error": "Refunds cannot be deleted."}, status=status.HTTP_403_FORBIDDEN)
    

class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling payments related to writer requests, considering discounts.
    """
    queryset = RequestPayment.objects.all()
    serializer_class = RequestPaymentSerializer

    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """
        Process payment for an approved writer request, considering client discounts.

        Args:
            request (Request): The HTTP request object.
            pk (str): The primary key of the order.

        Returns:
            Response: A response confirming the payment processing.
        """
        try:
            order = Order.objects.get(id=pk)
            payment_method = request.data.get('payment_method')
            additional_cost = request.data.get('additional_cost')
            discount_code = request.data.get('discount_code', None)

            # Apply the discount if provided
            discounted_total = order.total_cost

            if discount_code:
                discount = Discount.objects.filter(code=discount_code).first()

                if not discount or not discount.is_valid():
                    return Response({"error": "Invalid or expired discount code."}, status=400)

                # Calculate the discount amount
                if discount.discount_type == 'percentage':
                    discounted_amount = (discount.value / 100) * discounted_total
                else:  # fixed discount
                    discounted_amount = discount.value

                # Apply the discount to the order's total cost
                discounted_total -= discounted_amount

            # Add the additional costs for pages/slide increases
            final_amount = discounted_total + additional_cost

            # Process payment
            payment = RequestPayment.objects.create(
                order=order,
                payment_method=payment_method,
                additional_cost=additional_cost,
                payment_for="page_increase",  # Could vary based on request type
            )

            # Update the order total
            order.total_cost = final_amount
            order.save()

            # Mark the order as paid
            order.is_paid = True
            order.save()

            # If a valid discount was applied, increment the usage count
            if discount_code:
                discount.increment_usage()

            return Response({"message": f"Payment processed successfully. Total: {final_amount}"}, status=200)
        
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=404)

        except ValidationError as e:
            return Response({"error": str(e)}, status=400)