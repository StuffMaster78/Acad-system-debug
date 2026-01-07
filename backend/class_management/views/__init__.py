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
    queryset = ClassInstallment.objects.select_related('bundle', 'payment_record')
    serializer_class = ClassInstallmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter installments based on user role."""
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        return self.queryset.filter(bundle__client=user)


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
    queryset = ExpressClass.objects.select_related('client', 'website', 'assigned_writer', 'created_by_admin')
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
        """Admin assigns a writer to an express class."""
        express_class = self.get_object()
        serializer = ExpressClassAssignWriterSerializer(data=request.data)
        
        if serializer.is_valid():
            writer = serializer.validated_data['writer']
            express_class.assigned_writer = writer
            express_class.assigned_at = timezone.now()
            express_class.save()
            return Response({'status': 'writer assigned'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_website(self):
        """Get website from request."""
        domain = self.request.get_host()
        try:
            return Website.objects.get(domain=domain)
        except Website.DoesNotExist:
            return None

