"""
Views for order payment management.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
import logging

from .models import OrderPayment, FailedPayment
from .serializers import TransactionSerializer
from .services.payment_service import OrderPaymentService
from orders.models import Order
from authentication.permissions import IsSuperadminOrAdmin
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

class OrderPaymentViewSet(viewsets.ModelViewSet):
    """
    Viewset for handling order payments, including refunds.
    Supports all payment types: standard orders, special orders, installments, classes, wallet loading.
    """
    queryset = OrderPayment.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]
    http_method_names = ["get", "post", "patch", "delete"]  # Limit methods if needed

    def get_queryset(self):
        """
        Filter payments based on payment_type and user role.
        
        Query params:
        - payment_type: Filter by payment type (standard, predefined_special, etc.)
        - order_id: Filter by order ID (for standard payments)
        - special_order_id: Filter by special order ID
        - class_purchase_id: Filter by class purchase ID
        - installment_id: Filter by installment ID (via related_object_id)
        """
        queryset = OrderPayment.objects.all()
        
        # Non-staff users only see their own payments
        if not self.request.user.is_staff:
            queryset = queryset.filter(client=self.request.user)
        
        # Filter by payment type
        payment_type = self.request.query_params.get('payment_type')
        if payment_type:
            queryset = queryset.filter(payment_type=payment_type)
        
        # Filter by order relationships
        order_id = self.request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(order_id=order_id, payment_type='standard')
        
        special_order_id = self.request.query_params.get('special_order_id')
        if special_order_id:
            queryset = queryset.filter(
                special_order_id=special_order_id,
                payment_type__in=['predefined_special', 'estimated_special', 'special_installment']
            )
        
        class_purchase_id = self.request.query_params.get('class_purchase_id')
        if class_purchase_id:
            queryset = queryset.filter(class_purchase_id=class_purchase_id, payment_type='class_payment')
        
        installment_id = self.request.query_params.get('installment_id')
        if installment_id:
            queryset = queryset.filter(
                related_object_id=installment_id,
                related_object_type='installment_payment',
                payment_type='special_installment'
            )
        
        return queryset.select_related('order', 'special_order', 'class_purchase', 'client', 'website')

    @action(detail=False, methods=['post'], url_path='orders/(?P<order_id>[^/.]+)/initiate')
    def initiate_payment(self, request, order_id=None):
        """
        Initiate payment for a standard order.
        
        Creates a payment record. Gateway integration will be added later.
        For now supports:
        - wallet: Processes immediately
        - manual: Creates pending record for admin processing
        
        Request body:
        {
            "payment_method": "wallet" | "manual" | "stripe" (future),
            "discount_code": "optional_discount_code"
        }
        """
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if order already has completed payment
        if order.payments.filter(status='completed').exists():
            return Response(
                {"error": "Order already has a completed payment."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment_method = request.data.get('payment_method', 'manual')
        discount_code = request.data.get('discount_code')
        
        try:
            # Create payment record
            payment = OrderPaymentService.create_payment(
                order=order,
                client=request.user,
                payment_method=payment_method,
                discount_code=discount_code,
            )
            
            # Process wallet payment immediately if method is wallet
            if payment_method == 'wallet':
                try:
                    payment = OrderPaymentService.process_wallet_payment(payment)
                    return Response(
                        {
                            "message": "Payment processed successfully.",
                            "payment_id": payment.id,
                            "status": payment.status,
                            "transaction_id": payment.transaction_id,
                            "payment_identifier": OrderPaymentService.get_payment_identifier(payment)
                        },
                        status=status.HTTP_200_OK
                    )
                except ValueError as e:
                    # Wallet payment failed - payment record remains as 'pending'
                    return Response(
                        {"error": str(e), "payment_id": payment.id},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # For other methods (manual/stripe), return pending payment
            # Gateway integration will handle confirmation later
            return Response(
                {
                    "message": "Payment initiated. Waiting for confirmation.",
                    "payment_id": payment.id,
                    "status": payment.status,
                    "transaction_id": payment.transaction_id,
                    "payment_identifier": OrderPaymentService.get_payment_identifier(payment),
                    "note": "For gateway payments, confirmation will come via webhook."
                },
                status=status.HTTP_201_CREATED
            )
            
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error initiating payment: {str(e)}", exc_info=True)
            return Response(
                {"error": "An error occurred while processing payment."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def by_type(self, request):
        """
        Get payments filtered by type with proper identification.
        
        Query params:
        - payment_type: Required. One of: standard, predefined_special, estimated_special, 
                       special_installment, class_payment, wallet_loading
        - Additional filters based on type:
          - For standard: order_id
          - For special orders: special_order_id
          - For installments: installment_id
          - For classes: class_purchase_id
        """
        payment_type = request.query_params.get('payment_type')
        if not payment_type:
            return Response(
                {'error': 'payment_type query parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payments = self.get_queryset().filter(payment_type=payment_type)
        
        # Serialize with identifiers
        serializer = self.get_serializer(payments, many=True)
        data = serializer.data
        
        # Add payment identifiers to each payment
        for payment_data, payment_obj in zip(data, payments):
            payment_data['identifier'] = OrderPaymentService.get_payment_identifier(payment_obj)
        
        return Response(data, status=status.HTTP_200_OK)

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
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def list(self, request, *args, **kwargs):
        """
        List payments with identification info included.
        """
        response = super().list(request, *args, **kwargs)
        
        # Add identifiers to each payment
        if response.status_code == 200:
            payments = self.get_queryset()
            for i, payment_data in enumerate(response.data.get('results', response.data)):
                if isinstance(payment_data, dict):
                    try:
                        payment_obj = payments[i] if hasattr(response.data, '__iter__') and not isinstance(response.data, dict) else None
                        if payment_obj:
                            payment_data['identifier'] = OrderPaymentService.get_payment_identifier(payment_obj)
                    except (IndexError, TypeError):
                        pass
        
        return response

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a payment with full identification info.
        """
        response = super().retrieve(request, *args, **kwargs)
        
        if response.status_code == 200:
            payment = self.get_object()
            response.data['identifier'] = OrderPaymentService.get_payment_identifier(payment)
        
        return response
