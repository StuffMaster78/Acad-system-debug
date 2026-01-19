from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db import models
import logging

from class_management.models import (
    ClassPurchase, ClassInstallment, ClassBundleConfig, ClassBundle, ClassBundleFile, ExpressClass
)
from class_management.serializers import (
    ClassPurchaseSerializer, ClassInstallmentSerializer,
    ClassBundleConfigSerializer, ClassBundleSerializer,
    AdminCreateClassBundleSerializer, AdminConfigureInstallmentsSerializer,
    ExpressClassSerializer, ExpressClassCreateSerializer,
    ExpressClassScopeReviewSerializer, ExpressClassAssignWriterSerializer,
    ClassBundleAssignWriterSerializer
)
from class_management.services.class_purchases import handle_purchase_request
from class_management.services.pricing import get_class_price, InvalidPricingError
from class_management.services.class_bundle_admin import ClassBundleAdminService
from class_management.services.class_payment_processor import ClassPaymentProcessor
from class_management.services.class_communication import ClassBundleCommunicationService
from class_management.services.class_tickets import ClassBundleTicketService
from websites.models import Website
from communications.models import CommRole

logger = logging.getLogger(__name__)


class ClassBundleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing class bundles.
    Clients can view their bundles, admins can create and manage all bundles.
    """
    queryset = ClassBundle.objects.select_related('client', 'website', 'config', 'created_by_admin', 'assigned_writer').prefetch_related('installments', 'files')
    serializer_class = ClassBundleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter bundles based on user role."""
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        # Clients see their bundles, writers see assigned bundles
        return self.queryset.filter(
            models.Q(client=user) | models.Q(assigned_writer=user)
        ).distinct()

    def get_website(self):
        """Get website from request."""
        domain = self.request.get_host()
        try:
            return Website.objects.get(domain=domain)
        except Website.DoesNotExist:
            return None

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create' and self.request.user.is_staff:
            return AdminCreateClassBundleSerializer
        return ClassBundleSerializer

    def perform_create(self, serializer):
        """Handle bundle creation with admin or client context."""
        user = self.request.user
        website = self.get_website()
        
        if user.is_staff:
            # Admin creating bundle
            serializer.save(created_by_admin=user, website=website)
        else:
            # Client creating bundle (if allowed)
            serializer.save(client=user, website=website)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def configure_installments(self, request, pk=None):
        """Admin endpoint to configure installments for a bundle."""
        bundle = self.get_object()
        serializer = AdminConfigureInstallmentsSerializer(data=request.data)
        
        if serializer.is_valid():
            ClassBundleAdminService.configure_installments(
                bundle=bundle,
                installment_config=serializer.validated_data,
                admin_user=request.user
            )
            return Response({'status': 'installments configured'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def assign_writer(self, request, pk=None):
        """Admin assigns a writer to a bundle."""
        bundle = self.get_object()
        serializer = ClassBundleAssignWriterSerializer(data=request.data)
        
        if serializer.is_valid():
            writer = serializer.validated_data['writer']
            ClassBundleAdminService.assign_writer(
                bundle=bundle,
                writer=writer,
                admin_user=request.user
            )
            return Response({'status': 'writer assigned'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def purchase(self, request, pk=None):
        """Client purchases a bundle."""
        bundle = self.get_object()
        try:
            purchase = handle_purchase_request(
                bundle=bundle,
                client=request.user,
                payment_method=request.data.get('payment_method', 'wallet')
            )
            serializer = ClassPurchaseSerializer(purchase)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ClassPurchaseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing class purchases.
    Clients see their purchases, admins see all.
    """
    queryset = ClassPurchase.objects.select_related('bundle', 'client', 'website')
    serializer_class = ClassPurchaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter purchases based on user role."""
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        return self.queryset.filter(client=user)


class ClassInstallmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing class installments.
    """
    queryset = ClassInstallment.objects.select_related('class_bundle', 'payment_record', 'paid_by')
    serializer_class = ClassInstallmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter installments based on user role."""
        user = self.request.user
        queryset = self.queryset
        
        # Filter by bundle if provided
        bundle_id = self.request.query_params.get('class_bundle')
        if bundle_id:
            queryset = queryset.filter(class_bundle_id=bundle_id)
        
        if user.is_staff or getattr(user, 'role', None) in ['admin', 'superadmin', 'support']:
            return queryset
        return queryset.filter(class_bundle__client=user)
    
    @action(detail=True, methods=['post'], url_path='pay')
    def pay_installment(self, request, pk=None):
        """
        Process payment for a class installment.
        """
        from rest_framework.response import Response
        from rest_framework import status
        from rest_framework.exceptions import ValidationError
        from class_management.services.class_payment_processor import ClassPaymentProcessor
        
        installment = self.get_object()
        user = request.user
        
        # Check if already paid
        if installment.is_paid:
            return Response(
                {'error': 'This installment has already been paid.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permissions (client must own the bundle, or admin)
        if not (user.is_staff or getattr(user, 'role', None) in ['admin', 'superadmin', 'support']):
            if installment.class_bundle.client != user:
                return Response(
                    {'error': 'You do not have permission to pay for this installment.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        payment_method = request.data.get('payment_method', 'wallet')
        
        try:
            # Process payment
            payment = ClassPaymentProcessor.process_installment_payment(
                installment=installment,
                client=user if installment.class_bundle.client == user else installment.class_bundle.client,
                payment_method=payment_method
            )
            
            # Mark installment as paid
            installment.is_paid = True
            installment.paid_at = timezone.now()
            installment.paid_by = user if installment.class_bundle.client == user else installment.class_bundle.client
            installment.payment_record = payment
            installment.save()
            
            # Reload installment with updated data
            installment.refresh_from_db()
            
            serializer = self.get_serializer(installment)
            return Response({
                'message': 'Installment paid successfully.',
                'installment': serializer.data,
                'payment': {
                    'id': payment.id,
                    'reference_id': payment.reference_id,
                    'amount': str(payment.amount),
                    'status': payment.payment_status
                }
            }, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing installment payment: {e}", exc_info=True)
            return Response(
                {'error': 'Failed to process payment. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ClassBundleConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing class bundle configurations.
    Admin only.
    """
    queryset = ClassBundleConfig.objects.all()
    serializer_class = ClassBundleConfigSerializer
    permission_classes = [IsAdminUser]


class ExpressClassViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing express classes.
    """
    queryset = ExpressClass.objects.select_related(
        'client', 'website', 'assigned_writer', 'created_by_admin', 'reviewed_by'
    )
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ExpressClassCreateSerializer
        return ExpressClassSerializer

    def get_queryset(self):
        """Filter express classes based on user role."""
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        # Clients see their classes, writers see assigned classes
        return self.queryset.filter(
            models.Q(client=user) | models.Q(assigned_writer=user)
        ).distinct()

    def perform_create(self, serializer):
        """Handle express class creation."""
        user = self.request.user
        website = self.get_website()
        
        if user.is_staff:
            serializer.save(created_by_admin=user, website=website)
        else:
            serializer.save(client=user, website=website)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def review_scope(self, request, pk=None):
        """Admin reviews and sets scope for an express class."""
        express_class = self.get_object()
        serializer = ExpressClassScopeReviewSerializer(data=request.data)
        
        if serializer.is_valid():
            express_class.scope_reviewed = True
            express_class.scope_reviewed_at = timezone.now()
            express_class.scope_reviewed_by = request.user
            express_class.scope_notes = serializer.validated_data.get('scope_notes', '')
            express_class.save()
            return Response({'status': 'scope reviewed'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def assign_writer(self, request, pk=None):
        """Admin assigns a writer to an express class and creates a bonus."""
        from django.db import transaction
        from special_orders.models import WriterBonus
        from websites.utils import get_current_website
        from accounts.models import User
        
        express_class = self.get_object()
        serializer = ExpressClassAssignWriterSerializer(data=request.data)
        
        if serializer.is_valid():
            writer_id = serializer.validated_data['writer_id']
            bonus_amount = serializer.validated_data['bonus_amount']
            admin_notes = serializer.validated_data.get('admin_notes', '')
            
            try:
                writer = User.objects.get(id=writer_id)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Writer not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            website = get_current_website(request) or express_class.website
            
            with transaction.atomic():
                # Assign writer
                express_class.assigned_writer = writer
                express_class.assigned_at = timezone.now()
                express_class.status = 'assigned'
                express_class.save()
                
                # Create WriterBonus for the class payment
                WriterBonus.objects.create(
                    website=website,
                    writer=writer,
                    special_order=None,  # Express classes don't have special orders
                    amount=bonus_amount,
                    category='express_class',
                    reason=f"Payment for Express Class #{express_class.id}: {express_class.course or 'Class'}",
                    admin_notes=admin_notes,
                    is_paid=False,
                )
            
            return Response({
                'status': 'writer assigned',
                'bonus_created': True,
                'bonus_amount': str(bonus_amount)
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser], url_path='approval-queue')
    def approval_queue(self, request):
        """
        Get all express classes awaiting approval/review.
        Returns classes with status 'inquiry' or 'scope_review'.
        """
        from django.db import models as db_models
        
        queryset = self.get_queryset().filter(
            status__in=['inquiry', 'scope_review']
        ).order_by('created_at')
        
        # Apply filters
        website_id = request.query_params.get('website')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_website(self):
        """Get website from request."""
        domain = self.request.get_host()
        try:
            return Website.objects.get(domain=domain)
        except Website.DoesNotExist:
            return None

