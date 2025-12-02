"""
ViewSets for Enhanced Disputes
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from support_management.models.enhanced_disputes import OrderDispute, DisputeMessage
from support_management.serializers.enhanced_disputes import (
    OrderDisputeSerializer, OrderDisputeCreateSerializer, OrderDisputeUpdateSerializer,
    OrderDisputeEscalateSerializer, OrderDisputeResolveSerializer,
    DisputeMessageSerializer, DisputeMessageCreateSerializer
)
from support_management.permissions import IsSupportAgent
from orders.models import Order


class OrderDisputeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing order disputes.
    """
    queryset = OrderDispute.objects.select_related(
        'order', 'raised_by', 'other_party', 'assigned_to',
        'resolved_by', 'escalated_to', 'website'
    ).prefetch_related('messages').all()
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return OrderDisputeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderDisputeUpdateSerializer
        return OrderDisputeSerializer
    
    def get_queryset(self):
        """Filter disputes based on user role."""
        user = self.request.user
        qs = super().get_queryset()
        
        # Filter by website
        if hasattr(user, 'website') and user.website:
            qs = qs.filter(website=user.website)
        
        # Clients and writers can only see disputes they're involved in
        if user.role in ['client', 'writer']:
            qs = qs.filter(Q(raised_by=user) | Q(other_party=user))
        
        # Support, admin, superadmin can see all disputes
        elif user.role in ['support', 'admin', 'superadmin']:
            pass  # No additional filtering
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        
        # Filter by priority if provided
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            qs = qs.filter(priority=priority_filter)
        
        # Filter by order if provided
        order_id = self.request.query_params.get('order')
        if order_id:
            qs = qs.filter(order_id=order_id)
        
        return qs.order_by('-priority', '-created_at')
    
    def perform_create(self, serializer):
        """Create dispute with proper validation."""
        serializer.save()
    
    @action(detail=True, methods=['post'], serializer_class=OrderDisputeEscalateSerializer)
    def escalate(self, request, pk=None):
        """Escalate dispute to admin/superadmin."""
        dispute = self.get_object()
        
        # Check permissions
        if request.user.role not in ['support', 'admin', 'superadmin']:
            return Response(
                {'error': 'Only support staff can escalate disputes.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = OrderDisputeEscalateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        dispute.escalate(
            escalated_to=serializer.validated_data['escalated_to'],
            reason=serializer.validated_data.get('escalation_reason', '')
        )
        
        return Response(
            OrderDisputeSerializer(dispute).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], serializer_class=OrderDisputeResolveSerializer)
    def resolve(self, request, pk=None):
        """Resolve dispute."""
        dispute = self.get_object()
        
        # Check permissions
        if request.user.role not in ['support', 'admin', 'superadmin']:
            return Response(
                {'error': 'Only support staff can resolve disputes.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = OrderDisputeResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        dispute.resolve(
            resolved_by=request.user,
            resolution_notes=serializer.validated_data['resolution_notes'],
            outcome=serializer.validated_data['resolution_outcome']
        )
        
        return Response(
            OrderDisputeSerializer(dispute).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close dispute (final state)."""
        dispute = self.get_object()
        
        # Check permissions
        if request.user.role not in ['support', 'admin', 'superadmin']:
            return Response(
                {'error': 'Only support staff can close disputes.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if dispute.status != 'resolved':
            return Response(
                {'error': 'Dispute must be resolved before closing.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dispute.close()
        
        return Response(
            OrderDisputeSerializer(dispute).data,
            status=status.HTTP_200_OK
        )


class DisputeMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing dispute messages.
    """
    queryset = DisputeMessage.objects.select_related('dispute', 'sender').all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return DisputeMessageCreateSerializer
        return DisputeMessageSerializer
    
    def get_queryset(self):
        """Filter messages based on user role and dispute access."""
        user = self.request.user
        qs = super().get_queryset()
        
        # Filter by dispute if provided
        dispute_id = self.request.query_params.get('dispute')
        if dispute_id:
            qs = qs.filter(dispute_id=dispute_id)
        
        # Clients and writers can only see messages in disputes they're involved in
        if user.role in ['client', 'writer']:
            qs = qs.filter(
                dispute__raised_by=user
            ) | qs.filter(
                dispute__other_party=user
            )
            # Hide internal messages from non-staff
            qs = qs.exclude(is_internal=True)
        
        # Support, admin, superadmin can see all messages
        elif user.role in ['support', 'admin', 'superadmin']:
            pass  # No additional filtering
        
        return qs.order_by('created_at')
    
    def perform_create(self, serializer):
        """Create message with sender from request."""
        serializer.save(sender=self.request.user)

