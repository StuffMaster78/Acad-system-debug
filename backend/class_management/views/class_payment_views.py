"""
Streamlined views for class payment management.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from class_management.class_payment import ClassPayment, ClassWriterPayment
from class_management.models import ClassBundle
from class_management.serializers.class_payment import (
    ClassPaymentDetailSerializer, ClassPaymentSummarySerializer
)
from class_management.services.class_payment_service import ClassPaymentService

logger = logging.getLogger(__name__)


class ClassPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing class payment details.
    Provides streamlined access to payment and installment information.
    """
    permission_classes = [IsAuthenticated]
    queryset = ClassPayment.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ClassPaymentSummarySerializer
        return ClassPaymentDetailSerializer
    
    def get_queryset(self):
        """Filter payments based on user role."""
        user = self.request.user
        queryset = ClassPayment.objects.select_related(
            'class_bundle', 'website', 'assigned_writer'
        ).prefetch_related(
            'payment_installments__class_installment',
            'payment_installments__payment_record',
            'writer_payments__writer_bonus'
        )
        
        if user.is_superuser or getattr(user, 'role', None) in ['admin', 'superadmin']:
            return queryset
        
        if getattr(user, 'role', None) == 'writer':
            return queryset.filter(assigned_writer=user)
        
        if getattr(user, 'role', None) == 'client':
            return queryset.filter(class_bundle__client=user)
        
        return queryset.none()
    
    @action(detail=False, methods=['get'], url_path='writer/(?P<writer_id>[^/.]+)')
    def by_writer(self, request, writer_id=None):
        """Get all class payments for a specific writer."""
        if not request.user.is_staff:
            writer_id = request.user.id
        
        payments = ClassPaymentService.get_writer_class_payments(writer_id)
        serializer = ClassPaymentSummarySerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='bundle/(?P<bundle_id>[^/.]+)')
    def by_bundle(self, request, bundle_id=None):
        """Get payment details for a specific bundle."""
        details = ClassPaymentService.get_payment_details(bundle_id)
        
        if not details:
            return Response(
                {'error': 'Bundle not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        payment = details['payment']
        user = request.user
        
        if not user.is_staff:
            if getattr(user, 'role', None) == 'writer' and payment.assigned_writer != user:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            if getattr(user, 'role', None) == 'client' and payment.class_bundle.client != user:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = ClassPaymentDetailSerializer(payment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def refresh_status(self, request, pk=None):
        """Manually refresh payment status (admin only)."""
        payment = self.get_object()
        ClassPaymentService._update_payment_status(payment)
        serializer = ClassPaymentDetailSerializer(payment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def schedule_writer_payment(self, request, pk=None):
        """Manually schedule writer payment (admin only)."""
        payment = self.get_object()
        ClassPaymentService._schedule_writer_payment(payment)
        serializer = ClassPaymentDetailSerializer(payment, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def award_writer_payment(self, request, pk=None):
        """
        Award payment to writer for this class bundle (streamlined).
        
        Request body:
        {
            "amount": 150.00,  // Optional, uses class_payment.writer_compensation_amount if not provided
            "add_to_wallet": true  // If true, add directly to writer's wallet
        }
        """
        payment = self.get_object()
        amount = request.data.get('amount')
        add_to_wallet = request.data.get('add_to_wallet', False)
        
        from writer_management.services.writer_payment_award_service import WriterPaymentAwardService
        from websites.utils import get_current_website
        
        website = get_current_website(request) or payment.website
        
        try:
            from decimal import Decimal
            amount_decimal = Decimal(str(amount)) if amount else None
            
            result = WriterPaymentAwardService.award_class_payment(
                class_payment_id=payment.id,
                amount=amount_decimal,
                add_to_wallet=add_to_wallet,
                website=website,
                admin_user=request.user
            )
            
            serializer = ClassPaymentDetailSerializer(payment, context={'request': request})
            return Response({
                'payment': serializer.data,
                'awarded': result,
            })
        except Exception as e:
            logger.exception(f"Error awarding class payment: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

