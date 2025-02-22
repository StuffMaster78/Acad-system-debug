from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Avg, Count, F, Q  # Fix: Import Q and F here
from .models import Ticket, TicketMessage, TicketLog, TicketStatistics
from .serializers import (
    TicketSerializer, TicketCreateSerializer, TicketUpdateSerializer,
    TicketMessageSerializer, TicketMessageCreateSerializer,
    TicketLogSerializer, TicketStatisticsSerializer
)

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related('created_by', 'assigned_to', 'website').prefetch_related('messages', 'logs')
    serializer_class = TicketSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return different serializers based on action."""
        if self.action == 'create':
            return TicketCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TicketUpdateSerializer
        return TicketSerializer

    def perform_create(self, serializer):
        """Auto-assign ticket creator and save."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        """Escalate ticket to high priority."""
        ticket = self.get_object()
        ticket.is_escalated = True
        ticket.priority = 'critical'
        ticket.save()
        TicketLog.objects.create(ticket=ticket, action="Ticket escalated", performed_by=request.user)
        return Response({'status': 'Ticket escalated'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign a ticket to a support agent."""
        ticket = self.get_object()
        agent_id = request.data.get('assigned_to')
        if not agent_id:
            return Response({'error': 'Assigned user ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        ticket.assigned_to_id = agent_id
        ticket.save()
        TicketLog.objects.create(ticket=ticket, action=f"Assigned to user {agent_id}", performed_by=request.user)
        return Response({'status': 'Ticket assigned'}, status=status.HTTP_200_OK)

class TicketMessageViewSet(viewsets.ModelViewSet):
    queryset = TicketMessage.objects.select_related('ticket', 'sender')
    serializer_class = TicketMessageSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return TicketMessageCreateSerializer
        return TicketMessageSerializer

    def perform_create(self, serializer):
        """Auto-assign sender and save."""
        ticket = serializer.validated_data['ticket']
        serializer.save(sender=self.request.user)
        TicketLog.objects.create(ticket=ticket, action="New message added", performed_by=self.request.user)

        # Optionally notify assigned admin/support
        if ticket.assigned_to:
            # Send notification to assigned user
            pass  # Placeholder for future notification logic

        return Response({'status': 'Message added'}, status=status.HTTP_201_CREATED)

class TicketLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TicketLog.objects.select_related('ticket', 'performed_by')
    serializer_class = TicketLogSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']

class TicketStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TicketStatistics.objects.all()
    serializer_class = TicketStatisticsSerializer

    @action(detail=False, methods=['get'])
    def generate_statistics(self, request):
        """Dynamically generate ticket statistics."""
        stats = Ticket.objects.aggregate(
            total_tickets=Count('id'),
            resolved_tickets=Count('id', filter=Q(status='closed')),
            avg_resolution_time=Avg(F('resolution_time') - F('created_at'))  # Fix: Using F() expressions correctly
        )
        return Response(stats, status=status.HTTP_200_OK)