from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Avg, Count, F, Q
from .models import (
    Ticket, TicketMessage, TicketLog, 
    TicketStatistics, TicketAttachment
)
from .serializers import (
    TicketSerializer, TicketCreateSerializer, TicketUpdateSerializer,
    TicketMessageSerializer, TicketMessageCreateSerializer,
    TicketLogSerializer, TicketStatisticsSerializer,
    TicketAttachmentSerializer
)
from .permissions import IsAdminOrSupportForAttachment 
from notifications_system.services.dispatcher import notify_user

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related(
        'created_by', 'assigned_to', 'website'
    ).prefetch_related('messages', 'logs')
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

    def get_queryset(self):
        """Filter tickets based on user role."""
        user = self.request.user
        qs = super().get_queryset()
        if getattr(user, 'role', None) in ['writer', 'client']:
            return qs.filter(created_by=user)
        return qs
    
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
        TicketLog.objects.create(
            ticket=ticket,
            action="Ticket escalated",
            performed_by=request.user
        )
        # Notify all admins/support (example: all users with role 'admin' or 'support')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admins = User.objects.filter(role__in=['admin', 'support', 'superadmin'])
        for admin in admins:
            if admin != request.user:
                notify_user(
                    recipient=admin,
                    verb="Ticket escalated",
                    description=f"Ticket '{ticket.title}' has been escalated.",
                    target=ticket,
                    actor=request.user,
                    extra_data={"ticket_id": ticket.id}
                )
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
        TicketLog.objects.create(
            ticket=ticket,
            action=f"Assigned to user {agent_id}",
            performed_by=request.user
        )
        # Notify the new assignee
        if ticket.assigned_to and ticket.assigned_to != request.user:
            notify_user(
                recipient=ticket.assigned_to,
                verb="Ticket assigned",
                description=f"You have been assigned ticket '{ticket.title}'.",
                target=ticket,
                actor=request.user,
                extra_data={"ticket_id": ticket.id}
            )
        return Response({'status': 'Ticket assigned'}, status=status.HTTP_200_OK)
    
    def perform_update(self, serializer):
        """Notify creator if ticket is closed."""
        instance = serializer.save()
        if 'status' in serializer.validated_data and serializer.validated_data['status'] == 'closed':
            if instance.created_by and instance.created_by != self.request.user:
                notify_user(
                    recipient=instance.created_by,
                    verb="Ticket closed",
                    description=f"Your ticket '{instance.title}' has been closed.",
                    target=instance,
                    actor=self.request.user,
                    extra_data={"ticket_id": instance.id}
                )

class TicketMessageViewSet(viewsets.ModelViewSet):
    queryset = TicketMessage.objects.select_related('ticket', 'sender')
    serializer_class = TicketMessageSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return TicketMessageCreateSerializer
        return TicketMessageSerializer

    def perform_create(self, serializer):
        """
        Auto-assign sender and save.
        Also create a log entry for the ticket and notify assigned admin/support.
        """
        ticket = serializer.validated_data['ticket']
        message = serializer.save(sender=self.request.user)
        assigned_to = ticket.assigned_to
        # Create a log entry for the ticket
        if not assigned_to:
            assigned_to = ticket.created_by
        if not assigned_to:
            assigned_to = self.request.user
        TicketLog.objects.create(
            ticket=ticket,
            action="New message added",
            performed_by=self.request.user
        )
        # Notify assigned admin/support if not the sender
        if assigned_to and assigned_to != self.request.user:
            notify_user(
                recipient=assigned_to,
                verb="New ticket message",
                description=f"You have a new message on ticket '{ticket.title}'.",
                target=ticket,
                actor=self.request.user,
                extra_data={
                    "ticket_id": ticket.id,
                    "message_id": message.id,
                }
            )

        # Notify ticket creator if not the sender and not the assigned_to
        if ticket.created_by and ticket.created_by not in [self.request.user, assigned_to]:
            notify_user(
                recipient=ticket.created_by,
                verb="New ticket message",
                description=f"You have a new message on your ticket '{ticket.title}'.",
                target=ticket,
                actor=self.request.user,
                extra_data={
                    "ticket_id": ticket.id,
                    "message_id": message.id,
                }
            )

    def get_queryset(self):
        """
        Filter messages based on user role.
        Writers and clients can only see their own messages.
        Admins and support can see all messages.
        """
        user = self.request.user
        qs = super().get_queryset()
        if getattr(user, 'role', None) in ['writer', 'client']:
            return qs.filter(sender=user)
        return qs

class TicketAttachmentViewSet(viewsets.ModelViewSet):
    queryset = TicketAttachment.objects.select_related('ticket', 'uploaded_by')
    serializer_class = TicketAttachmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['ticket__title', 'uploaded_by__username']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """Auto-assign uploader and save, notify assigned user."""
        attachment = serializer.save(uploaded_by=self.request.user)
        TicketLog.objects.create(
            ticket=attachment.ticket,
            action="File uploaded",
            performed_by=self.request.user
        )
        assigned_to = attachment.ticket.assigned_to
        if assigned_to and assigned_to != self.request.user:
            notify_user(
                recipient=assigned_to,
                verb="New ticket attachment",
                description=f"A new file was attached to ticket '{attachment.ticket.title}'.",
                target=attachment.ticket,
                actor=self.request.user,
                extra_data={"ticket_id": attachment.ticket.id, "attachment_id": attachment.id}
            )

    def get_permissions(self):
        if self.action == 'retrieve':
            return [IsAdminOrSupportForAttachment()]
        return super().get_permissions()
    
    def get_queryset(self):
        """
        Filter attachments based on user role.
        Writers and clients can only see their own attachments.
        Admins and support can see all attachments.
        """
        user = self.request.user
        qs = super().get_queryset()
        if getattr(user, 'role', None) in ['writer', 'client']:
            return qs.filter(uploaded_by=user)
        return qs

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
            avg_resolution_time=Avg(F('resolution_time') - F('created_at'))
        )
        return Response(stats, status=status.HTTP_200_OK)