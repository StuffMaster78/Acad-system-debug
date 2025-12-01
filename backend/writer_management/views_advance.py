from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils.timezone import now
from decimal import Decimal

from writer_management.models import WriterProfile
from writer_management.models.advance_payment import WriterAdvancePaymentRequest
from writer_management.serializers_advance import (
    WriterAdvancePaymentRequestSerializer,
    AdvanceRequestCreateSerializer,
    AdvanceEligibilitySerializer,
    AdvanceApproveSerializer,
    AdvanceRejectSerializer
)
from writer_management.services.advance_payment_service import AdvancePaymentService
from writer_management.permissions import IsWriter, IsAdminOrSuperAdmin
from websites.models import Website
from notifications_system.services.dispatch import send
from notifications_system.enums import NotificationType

class WriterAdvancePaymentRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing advance payment requests.
    Writers can create requests, admins can approve/reject with counteroffers.
    """
    serializer_class = WriterAdvancePaymentRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        website_id = self.request.query_params.get('website') or self.request.headers.get('X-Website')
        
        if not website_id:
            return WriterAdvancePaymentRequest.objects.none()
        
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return WriterAdvancePaymentRequest.objects.none()
        
        # Writers see only their requests
        if user.role == 'writer':
            try:
                writer_profile = WriterProfile.objects.get(user=user, website=website)
                return WriterAdvancePaymentRequest.objects.filter(
                    writer=writer_profile,
                    website=website
                ).select_related('writer', 'writer__user', 'reviewed_by', 'disbursed_by', 'website')
            except WriterProfile.DoesNotExist:
                return WriterAdvancePaymentRequest.objects.none()
        
        # Admins see all requests
        elif user.role in ['admin', 'superadmin']:
            queryset = WriterAdvancePaymentRequest.objects.filter(website=website)
            
            # Filter by status if provided
            status_filter = self.request.query_params.get('status')
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            # Filter by writer if provided
            writer_id = self.request.query_params.get('writer')
            if writer_id:
                queryset = queryset.filter(writer_id=writer_id)
            
            return queryset.select_related('writer', 'writer__user', 'reviewed_by', 'disbursed_by', 'website')
        
        return WriterAdvancePaymentRequest.objects.none()
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['eligibility', 'request_advance']:
            return [IsAuthenticated(), IsWriter()]
        elif self.action in ['approve', 'reject', 'disburse']:
            return [IsAuthenticated(), IsAdminOrSuperAdmin()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def eligibility(self, request):
        """Get advance eligibility information for current writer"""
        if request.user.role != 'writer':
            return Response(
                {'detail': 'Only writers can check eligibility'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        website_id = request.query_params.get('website') or request.headers.get('X-Website')
        if not website_id:
            return Response(
                {'detail': 'Website parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            website = Website.objects.get(id=website_id)
            writer_profile = WriterProfile.objects.get(user=request.user, website=website)
        except (Website.DoesNotExist, WriterProfile.DoesNotExist):
            return Response(
                {'detail': 'Writer profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        eligibility = AdvancePaymentService.calculate_max_advance(writer_profile, website)
        serializer = AdvanceEligibilitySerializer(eligibility)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def request_advance(self, request):
        """Create a new advance payment request"""
        if request.user.role != 'writer':
            return Response(
                {'detail': 'Only writers can request advances'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        website_id = request.data.get('website') or request.query_params.get('website') or request.headers.get('X-Website')
        if not website_id:
            return Response(
                {'detail': 'Website parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            website = Website.objects.get(id=website_id)
            writer_profile = WriterProfile.objects.get(user=request.user, website=website)
        except (Website.DoesNotExist, WriterProfile.DoesNotExist):
            return Response(
                {'detail': 'Writer profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AdvanceRequestCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        requested_amount = Decimal(str(serializer.validated_data['amount']))
        reason = serializer.validated_data.get('reason', '')
        
        # Calculate eligibility
        eligibility = AdvancePaymentService.calculate_max_advance(writer_profile, website)
        
        if requested_amount > eligibility['available_advance']:
            return Response(
                {
                    'detail': f'Requested amount exceeds available advance. Maximum: ${eligibility["available_advance"]:.2f}',
                    'available_advance': str(eligibility['available_advance'])
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create request
        with transaction.atomic():
            advance_request = WriterAdvancePaymentRequest.objects.create(
                website=website,
                writer=writer_profile,
                requested_amount=requested_amount,
                reason=reason,
                expected_earnings=eligibility['expected_earnings'],
                max_advance_percentage=eligibility['max_percentage'],
                max_advance_amount=eligibility['max_advance_amount'],
                status='pending'
            )
        
        # Notify admins
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_users = User.objects.filter(
            role__in=['admin', 'superadmin'],
            is_active=True
        )
        if website:
            admin_users = admin_users.filter(website=website)
        
        for admin in admin_users[:50]:  # Limit to prevent spam
            send(
                user=admin,
                event="writer.advance_request.created",
                payload={
                    "advance_request_id": advance_request.id,
                    "writer_id": writer_profile.id,
                    "writer_username": writer_profile.user.username,
                    "requested_amount": str(requested_amount),
                    "reason": reason[:100] if reason else None,
                },
                website=website,
                channels=[NotificationType.IN_APP],
                category="advance_payments",
            )
        
        serializer = WriterAdvancePaymentRequestSerializer(advance_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve an advance payment request (admin only).
        Supports counteroffer - admin can approve a different amount than requested.
        """
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'detail': 'Only admins can approve advances'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        advance_request = self.get_object()
        
        if advance_request.status != 'pending':
            return Response(
                {'detail': f'Cannot approve request with status: {advance_request.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AdvanceApproveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get approved amount (counteroffer) or use requested amount
        approved_amount = serializer.validated_data.get('approved_amount')
        if approved_amount is None:
            approved_amount = advance_request.requested_amount
        else:
            approved_amount = Decimal(str(approved_amount))
        
        review_notes = serializer.validated_data.get('review_notes', '')
        
        # Validate approved amount
        if approved_amount <= 0:
            return Response(
                {'detail': 'Approved amount must be greater than zero'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if approved_amount > advance_request.max_advance_amount:
            return Response(
                {'detail': 'Approved amount exceeds maximum allowed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If counteroffer, add note explaining
        if approved_amount < advance_request.requested_amount:
            if not review_notes:
                review_notes = f'Counteroffer: Approved ${approved_amount:.2f} instead of requested ${advance_request.requested_amount:.2f}'
            else:
                review_notes = f'Counteroffer: ${approved_amount:.2f} (requested ${advance_request.requested_amount:.2f}). {review_notes}'
        
        with transaction.atomic():
            advance_request.approved_amount = approved_amount
            advance_request.status = 'approved'
            advance_request.reviewed_by = request.user
            advance_request.reviewed_at = now()
            advance_request.review_notes = review_notes
            advance_request.save()
        
        # Notify writer
        send(
            user=advance_request.writer.user,
            event="writer.advance_request.approved",
            payload={
                "advance_request_id": advance_request.id,
                "requested_amount": str(advance_request.requested_amount),
                "approved_amount": str(approved_amount),
                "is_counteroffer": approved_amount < advance_request.requested_amount,
                "review_notes": review_notes,
            },
            website=advance_request.website,
            channels=[NotificationType.IN_APP, NotificationType.EMAIL],
            category="advance_payments",
        )
        
        serializer = WriterAdvancePaymentRequestSerializer(advance_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject an advance payment request (admin only).
        Requires a reason for rejection.
        """
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'detail': 'Only admins can reject advances'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        advance_request = self.get_object()
        
        if advance_request.status != 'pending':
            return Response(
                {'detail': f'Cannot reject request with status: {advance_request.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AdvanceRejectSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        review_notes = serializer.validated_data['review_notes']
        
        if not review_notes or not review_notes.strip():
            return Response(
                {'detail': 'Rejection reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            advance_request.status = 'rejected'
            advance_request.reviewed_by = request.user
            advance_request.reviewed_at = now()
            advance_request.review_notes = review_notes
            advance_request.save()
        
        # Notify writer
        send(
            user=advance_request.writer.user,
            event="writer.advance_request.rejected",
            payload={
                "advance_request_id": advance_request.id,
                "requested_amount": str(advance_request.requested_amount),
                "rejection_reason": review_notes,
            },
            website=advance_request.website,
            channels=[NotificationType.IN_APP, NotificationType.EMAIL],
            category="advance_payments",
        )
        
        serializer = WriterAdvancePaymentRequestSerializer(advance_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def disburse(self, request, pk=None):
        """Disburse an approved advance (admin only)"""
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'detail': 'Only admins can disburse advances'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        advance_request = self.get_object()
        
        if advance_request.status != 'approved':
            return Response(
                {'detail': f'Can only disburse approved advances. Current status: {advance_request.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not advance_request.approved_amount:
            return Response(
                {'detail': 'Approved amount not set'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Disburse to writer wallet
        from writer_wallet.models import WriterWallet, WalletTransaction
        
        writer_wallet, _ = WriterWallet.objects.get_or_create(
            writer=advance_request.writer.user,
            website=advance_request.website
        )
        
        disbursed_amount = advance_request.approved_amount
        
        with transaction.atomic():
            # Credit wallet
            writer_wallet.balance += disbursed_amount
            writer_wallet.save()
            
            # Create transaction
            WalletTransaction.objects.create(
                writer_wallet=writer_wallet,
                website=advance_request.website,
                transaction_type='Adjustment',  # Or create new type 'Advance'
                amount=disbursed_amount,
                reference_code=f'ADV-{advance_request.id}'
            )
            
            # Update advance request
            advance_request.disbursed_amount = disbursed_amount
            advance_request.status = 'disbursed'
            advance_request.disbursed_by = request.user
            advance_request.disbursed_at = now()
            advance_request.save()
        
        # Notify writer
        send(
            user=advance_request.writer.user,
            event="writer.advance_request.disbursed",
            payload={
                "advance_request_id": advance_request.id,
                "disbursed_amount": str(disbursed_amount),
            },
            website=advance_request.website,
            channels=[NotificationType.IN_APP, NotificationType.EMAIL],
            category="advance_payments",
        )
        
        serializer = WriterAdvancePaymentRequestSerializer(advance_request)
        return Response(serializer.data)

