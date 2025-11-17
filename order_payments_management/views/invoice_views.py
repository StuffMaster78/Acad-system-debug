"""
Views for invoice management and payment processing.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404

from ..models import Invoice
from ..serializers import InvoiceSerializer, InvoiceCreateSerializer
from ..services.invoice_service import InvoiceService
from authentication.permissions import IsSuperadminOrAdmin
from websites.models import Website

logger = logging.getLogger(__name__)


class LimitedPagination(PageNumberPagination):
    """Custom pagination class with safety limits to prevent performance issues."""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500  # Safety limit to prevent excessive data transfer
    
    def get_paginated_response(self, data):
        """Return paginated response with metadata."""
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
        })


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing invoices.
    Allows admins/superadmins to create, view, update, and manage invoices.
    """
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]
    filter_backends = []
    pagination_class = LimitedPagination
    
    def get_queryset(self):
        """Filter invoices based on user role and website."""
        queryset = Invoice.objects.select_related(
            'client', 'website', 'issued_by', 'order', 'special_order', 'class_purchase'
        ).all()
        
        user = self.request.user
        
        # Filter by website if not superadmin
        if user.role != 'superadmin':
            website = getattr(user, 'website', None)
            if website:
                queryset = queryset.filter(website=website)
        
        # Filter by query parameters
        status_filter = self.request.query_params.get('status')
        if status_filter == 'paid':
            queryset = queryset.filter(is_paid=True)
        elif status_filter == 'unpaid':
            queryset = queryset.filter(is_paid=False)
        elif status_filter == 'overdue':
            queryset = queryset.filter(is_paid=False, due_date__lt=timezone.now().date())
        
        client_id = self.request.query_params.get('client_id')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(reference_id__icontains=search) |
                Q(recipient_email__icontains=search) |
                Q(title__icontains=search) |
                Q(order_number__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """Use different serializer for create vs other operations."""
        if self.action == 'create':
            return InvoiceCreateSerializer
        return InvoiceSerializer
    
    def perform_create(self, serializer):
        """Create invoice with payment link generation and optional email sending."""
        user = self.request.user
        data = self.request.data
        
        # Get website
        website_id = data.get('website_id')
        if not website_id:
            # Auto-assign website for non-superadmins
            if user.role != 'superadmin':
                website = getattr(user, 'website', None)
                if not website:
                    raise ValidationError({"website_id": "Website is required."})
            else:
                raise ValidationError({"website_id": "Website is required."})
        else:
            try:
                website = Website.objects.get(id=website_id, is_active=True, is_deleted=False)
            except Website.DoesNotExist:
                raise ValidationError({"website_id": "Invalid website ID."})
        
        # Validate website permissions
        if user.role != 'superadmin':
            user_website = getattr(user, 'website', None)
            if user_website and website != user_website:
                raise ValidationError({"website_id": "You can only create invoices for your assigned website."})
        
        # Get client if provided
        client = None
        client_id = data.get('client_id')
        if client_id:
            from users.models import User
            try:
                client = User.objects.get(id=client_id)
            except User.DoesNotExist:
                raise ValidationError({"client_id": "Invalid client ID."})
        
        # Get optional references
        order = None
        special_order = None
        class_purchase = None
        
        order_id = data.get('order')
        if order_id:
            from orders.models import Order
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                pass
        
        special_order_id = data.get('special_order')
        if special_order_id:
            from special_orders.models import SpecialOrder
            try:
                special_order = SpecialOrder.objects.get(id=special_order_id)
            except SpecialOrder.DoesNotExist:
                pass
        
        class_purchase_id = data.get('class_purchase')
        if class_purchase_id:
            from class_management.models import ClassPurchase
            try:
                class_purchase = ClassPurchase.objects.get(id=class_purchase_id)
            except ClassPurchase.DoesNotExist:
                pass
        
        # Create invoice via service
        send_email = data.get('send_email', True)
        invoice = InvoiceService.create_invoice(
            recipient_email=data.get('recipient_email', client.email if client else ''),
            website=website,
            amount=serializer.validated_data['amount'],
            title=serializer.validated_data['title'],
            due_date=serializer.validated_data['due_date'],
            issued_by=user,
            recipient_name=data.get('recipient_name', ''),
            purpose=data.get('purpose', ''),
            description=data.get('description', ''),
            order_number=data.get('order_number', ''),
            client=client,
            order=order,
            special_order=special_order,
            class_purchase=class_purchase,
            send_email=send_email,
        )
        
        # Return created invoice
        serializer.instance = invoice
    
    @action(detail=True, methods=['post'])
    def send_email(self, request, pk=None):
        """Resend invoice email."""
        invoice = self.get_object()
        
        success = InvoiceService.send_invoice_email(invoice)
        
        if success:
            return Response({
                "message": "Invoice email sent successfully",
                "email_sent_count": invoice.email_sent_count
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "Failed to send invoice email"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Manually mark invoice as paid (for manual payments)."""
        invoice = self.get_object()
        
        if invoice.is_paid:
            return Response({
                "error": "Invoice is already paid"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        invoice.is_paid = True
        invoice.paid_at = timezone.now()
        invoice.save(update_fields=['is_paid', 'paid_at'])
        
        # Send confirmation email
        try:
            InvoiceService.send_payment_confirmation_email(invoice)
        except Exception as e:
            logger.error(f"Failed to send payment confirmation email: {e}")
        
        return Response({
            "message": "Invoice marked as paid",
            "invoice": InvoiceSerializer(invoice).data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='pay/(?P<token>[^/.]+)')
    def get_invoice_by_token(self, request, token=None):
        """
        Public endpoint to get invoice details by payment token.
        Used for payment page (no authentication required).
        """
        invoice = InvoiceService.get_invoice_by_token(token)
        
        if not invoice:
            return Response({
                "error": "Invalid or expired payment link"
            }, status=status.HTTP_404_NOT_FOUND)
        
        if invoice.is_paid:
            return Response({
                "error": "Invoice has already been paid"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='pay/(?P<token>[^/.]+)', permission_classes=[AllowAny])
    def process_payment(self, request, token=None):
        """
        Public endpoint to process invoice payment.
        No authentication required (uses token for security).
        """
        invoice = InvoiceService.get_invoice_by_token(token)
        
        if not invoice:
            return Response({
                "error": "Invalid or expired payment link"
            }, status=status.HTTP_404_NOT_FOUND)
        
        if invoice.is_paid:
            return Response({
                "error": "Invoice has already been paid"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        payment_method = request.data.get('payment_method', 'wallet')
        payment_data = request.data.get('payment_data', {})
        
        try:
            payment = InvoiceService.process_invoice_payment(
                invoice=invoice,
                payment_method=payment_method,
                payment_data=payment_data
            )
            
            return Response({
                "message": "Payment processed successfully",
                "invoice": InvoiceSerializer(invoice).data,
                "payment_id": payment.id
            }, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Error processing invoice payment: {e}")
            return Response({
                "error": "Failed to process payment"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get invoice statistics - optimized with combined aggregations."""
        queryset = self.get_queryset()
        today = timezone.now().date()
        
        # Combined aggregation query - reduces from 7 queries to 2 queries
        # First query: Get all counts and amounts in one aggregation
        stats = queryset.aggregate(
            total_invoices=Count('id'),
            paid_invoices=Count('id', filter=Q(is_paid=True)),
            unpaid_invoices=Count('id', filter=Q(is_paid=False)),
            overdue_invoices=Count(
                'id',
                filter=Q(is_paid=False, due_date__lt=today)
            ),
            total_amount=Sum('amount'),
            paid_amount=Sum('amount', filter=Q(is_paid=True)),
            unpaid_amount=Sum('amount', filter=Q(is_paid=False)),
        )
        
        return Response({
            "total_invoices": stats['total_invoices'] or 0,
            "paid_invoices": stats['paid_invoices'] or 0,
            "unpaid_invoices": stats['unpaid_invoices'] or 0,
            "overdue_invoices": stats['overdue_invoices'] or 0,
            "total_amount": float(stats['total_amount'] or 0),
            "paid_amount": float(stats['paid_amount'] or 0),
            "unpaid_amount": float(stats['unpaid_amount'] or 0),
        }, status=status.HTTP_200_OK)

