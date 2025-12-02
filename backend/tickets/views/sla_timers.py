"""
ViewSets for Ticket SLA
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from tickets.sla_timers import TicketSLA
from tickets.serializers.sla_timers import (
    TicketSLASerializer, TicketSLACreateSerializer,
    TicketSLAMarkFirstResponseSerializer, TicketSLAMarkResolvedSerializer
)
from rest_framework import serializers
from tickets.models import Ticket
from admin_management.permissions import IsAdmin
from support_management.permissions import IsSupportAgent


class TicketSLAViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing ticket SLA tracking.
    """
    queryset = TicketSLA.objects.select_related('ticket', 'website').all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return TicketSLACreateSerializer
        return TicketSLASerializer
    
    def get_queryset(self):
        """Filter SLA records based on user role."""
        user = self.request.user
        qs = super().get_queryset()
        
        # Filter by website
        if hasattr(user, 'website') and user.website:
            qs = qs.filter(website=user.website)
        
        # Filter by ticket if provided
        ticket_id = self.request.query_params.get('ticket')
        if ticket_id:
            qs = qs.filter(ticket_id=ticket_id)
        
        # Filter by breached status
        breached = self.request.query_params.get('breached')
        if breached == 'true':
            qs = qs.filter(resolution_breached=True)
        elif breached == 'false':
            qs = qs.filter(resolution_breached=False)
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            qs = qs.filter(priority=priority)
        
        # Clients and writers can only see SLA for their own tickets
        if user.role in ['client', 'writer']:
            qs = qs.filter(ticket__created_by=user)
        
        # Support, admin, superadmin can see all
        elif user.role in ['support', 'admin', 'superadmin']:
            pass  # No additional filtering
        
        return qs.order_by('-resolution_deadline')
    
    def perform_create(self, serializer):
        """Create SLA tracking for a ticket."""
        ticket = serializer.validated_data['ticket']
        
        # Check if SLA already exists
        if TicketSLA.objects.filter(ticket=ticket).exists():
            raise serializers.ValidationError(
                'SLA tracking already exists for this ticket.'
            )
        
        # Create SLA using the class method
        sla = TicketSLA.create_for_ticket(ticket)
        serializer.instance = sla
    
    @action(detail=True, methods=['post'], serializer_class=TicketSLAMarkFirstResponseSerializer)
    def mark_first_response(self, request, pk=None):
        """Mark first response sent."""
        sla = self.get_object()
        
        # Check permissions
        if request.user.role not in ['support', 'admin', 'superadmin']:
            return Response(
                {'error': 'Only support staff can mark first response.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        sla.mark_first_response()
        
        return Response(
            TicketSLASerializer(sla).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], serializer_class=TicketSLAMarkResolvedSerializer)
    def mark_resolved(self, request, pk=None):
        """Mark ticket as resolved."""
        sla = self.get_object()
        
        # Check permissions
        if request.user.role not in ['support', 'admin', 'superadmin']:
            return Response(
                {'error': 'Only support staff can mark tickets as resolved.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        sla.mark_resolved()
        
        return Response(
            TicketSLASerializer(sla).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def check_breaches(self, request):
        """Check and update all SLA breach statuses."""
        if request.user.role not in ['support', 'admin', 'superadmin']:
            return Response(
                {'error': 'Only support staff can check breaches.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        slas = self.get_queryset()
        updated_count = 0
        
        for sla in slas:
            old_breached = sla.resolution_breached
            sla.check_and_update_breaches()
            if sla.resolution_breached != old_breached:
                updated_count += 1
        
        return Response({
            'message': f'Checked {slas.count()} SLA records, updated {updated_count} breach statuses.'
        })

