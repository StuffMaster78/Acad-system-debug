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
from notifications_system.services.core import NotificationService
from django.utils import timezone
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import (
    Count, Q, F, ExpressionWrapper, DurationField, Avg, Case, When
)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import logging

log = logging.getLogger(__name__)

# Backward-compatibility stub used by some tests that patch this symbol
def notify_user(*args, **kwargs):
    return True
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related(
        'created_by', 'assigned_to', 'website'
    ).prefetch_related('messages', 'logs')
    serializer_class = TicketSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    pagination_class = None
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
        user = self.request.user
        # If support/admin is creating a ticket, they can specify created_by (recipient)
        # Otherwise, set created_by to the request user
        if user.role in ['support', 'admin', 'superadmin']:
            # Support/admin can specify created_by in the request data
            created_by = serializer.validated_data.get('created_by')
            if not created_by:
                # If not specified, default to request user
                serializer.save(created_by=user)
            else:
                # Save with the specified recipient
                serializer.save()
        else:
            # For other roles, always set created_by to request user
            serializer.save(created_by=user)

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
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a ticket. Only admins, superadmins, support, and editors can close tickets."""
        ticket = self.get_object()
        user = request.user
        user_role = getattr(user, 'role', None)
        
        # Check permissions
        if user_role not in ['admin', 'superadmin', 'support', 'editor']:
            return Response(
                {'error': 'Only administrators, support staff, and editors can close tickets.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get optional reason/notes
        reason = request.data.get('reason', '')
        
        # Update ticket status
        old_status = ticket.status
        ticket.status = 'closed'
        ticket.resolution_time = timezone.now()
        ticket.save()
        
        # Create log entry
        action_text = f"Ticket closed by {user.username or user.email}"
        if reason:
            action_text += f": {reason}"
        TicketLog.objects.create(
            ticket=ticket,
            action=action_text,
            performed_by=user
        )
        
        # Notify ticket creator if they exist and aren't the one closing it
        if ticket.created_by and ticket.created_by != user:
            try:
                from notifications_system.services.notification_helper import NotificationHelper
                NotificationHelper.notify_ticket_closed(
                    ticket=ticket,
                    closed_by=user,
                    reason=reason
                )
            except Exception as e:
                log.exception(f"Failed to send ticket closed notification: {e}")
        
        return Response({
            'status': 'Ticket closed',
            'ticket': TicketSerializer(ticket).data,
            'old_status': old_status,
            'new_status': ticket.status
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """Reopen a closed ticket. Only admins, superadmins, support, and editors can reopen tickets."""
        ticket = self.get_object()
        user = request.user
        user_role = getattr(user, 'role', None)
        
        # Check permissions
        if user_role not in ['admin', 'superadmin', 'support', 'editor']:
            return Response(
                {'error': 'Only administrators, support staff, and editors can reopen tickets.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if ticket is closed
        if ticket.status != 'closed':
            return Response(
                {'error': f'Cannot reopen ticket with status "{ticket.status}". Only closed tickets can be reopened.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get optional reason/notes and target status
        reason = request.data.get('reason', '')
        target_status = request.data.get('status', 'open')  # Default to 'open', can be 'in_progress'
        
        # Validate target status
        valid_statuses = ['open', 'in_progress']
        if target_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status "{target_status}". Must be one of: {", ".join(valid_statuses)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update ticket status
        old_status = ticket.status
        ticket.status = target_status
        ticket.resolution_time = None  # Clear resolution time
        ticket.save()
        
        # Create log entry
        action_text = f"Ticket reopened by {user.username or user.email} (status: {target_status})"
        if reason:
            action_text += f": {reason}"
        TicketLog.objects.create(
            ticket=ticket,
            action=action_text,
            performed_by=user
        )
        
        # Notify ticket creator if they exist
        if ticket.created_by:
            try:
                from notifications_system.services.notification_helper import NotificationHelper
                NotificationHelper.notify_ticket_reopened(
                    ticket=ticket,
                    reopened_by=user,
                    reason=reason
                )
            except Exception as e:
                log.exception(f"Failed to send ticket reopened notification: {e}")
        
        return Response({
            'status': 'Ticket reopened',
            'ticket': TicketSerializer(ticket).data,
            'old_status': old_status,
            'new_status': ticket.status
        }, status=status.HTTP_200_OK)
    
    def perform_update(self, serializer):
        """
        On close -> notify the ticket creator (not the closer).
        Never block the update if notifications fail.
        """
        instance = serializer.save()

        new_status = serializer.validated_data.get("status")
        if new_status != "closed":
            return instance

        creator = getattr(instance, "created_by", None)
        actor_user = getattr(self.request, "user", None)

        # only notify if creator exists & isn’t the one closing it
        if not creator or (actor_user and creator.id == actor_user.id):
            return instance

        try:
            notify_user(
                recipient=creator,
                verb="Ticket closed",
                description=f"Your ticket '{instance.title}' has been closed.",
                target=instance,
                actor=actor_user,
                extra_data={"ticket_id": instance.id},
            )
        except Exception as exc:
            log.exception("Ticket close notification failed: %s", exc)

        return instance

class TicketMessageViewSet(viewsets.ModelViewSet):
    queryset = TicketMessage.objects.select_related('ticket', 'sender')
    serializer_class = TicketMessageSerializer
    pagination_class = None

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
        # Notify relevant users about the reply
        try:
            from notifications_system.services.notification_helper import NotificationHelper
            NotificationHelper.notify_ticket_reply(
                ticket=ticket,
                message=message,
                replier=self.request.user
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send ticket reply notification: {e}")

        # Legacy notification code (can be removed once fully migrated)
        # if assigned_to and assigned_to != self.request.user: ticket.created_by and ticket.created_by not in [self.request.user, assigned_to]:
            NotificationService.send_notification(
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
    queryset = TicketAttachment.objects.select_related(
        'ticket', 'uploaded_by', 'ticket__assigned_to',
        'ticket__created_by', 'ticket__website'
    )
    serializer_class = TicketAttachmentSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['ticket__title', 'uploaded_by__username']
    ordering_fields = ['uploaded_at']
    ordering = ['-uploaded_at']

    def perform_create(self, serializer):
        """
        Auto-assign uploader and save,
        notify assigned user (if not the uploader).
        Notification failure must not block the request.
        """
        attachment = serializer.save(uploaded_by=self.request.user)
        TicketLog.objects.create(
            ticket=attachment.ticket,
            action="File uploaded",
            performed_by=self.request.user
        )
        assigned_to = attachment.ticket.assigned_to
        if assigned_to and assigned_to != self.request.user:
            try:
                    NotificationService.send_notification(
                        event_key="communications.ticket_attachment_added",
                        website=getattr(attachment.ticket.website, "id", None),  # tenant-safe
                        actor={"type": "user", "id": self.request.user.id},
                        subject={"type": "ticket", "id": attachment.ticket.id},
                        user_ids=[assigned_to.id],  # explicit recipient
                        channels=["in_app", "email"],  # hint; prefs still apply
                        payload={
                            "ticket_id": attachment.ticket.id,
                            "ticket_title": attachment.ticket.title,
                            "attachment_id": attachment.id,
                            "uploaded_at": timezone.now().isoformat(),
                            "uploaded_by_user_id": self.request.user.id,
                        },
                        idempotency_key=(
                            f"ticket.attachment_added:"
                            f"{attachment.ticket.id}:{attachment.id}:{assigned_to.id}"
                        ),
                        async_send=True,  # Celery if configured
                    )
            except Exception as exc:
                log.exception("Attachment notify failed: %s", exc)

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

# --- Logs ---

class TicketLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        TicketLog.objects
        .select_related("ticket", "performed_by")
        .order_by("-timestamp")
    )
    serializer_class = TicketLogSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["timestamp"]
    ordering = ["-timestamp"]
    # Optional: throttle/paginate/permission here (recommended)


# --- Statistics ---

class TicketStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Exposes persisted snapshots via list/retrieve,
    and a dynamic aggregate via /generate/.
    """
    queryset = TicketStatistics.objects.all().order_by("-created_at")
    serializer_class = TicketStatisticsSerializer

    @method_decorator(cache_page(60))  # cache for 60s; tweak as needed
    @action(detail=False, methods=["get"], url_path="generate")
    def generate_statistics(self, request):
        """
        Dynamically compute ticket KPIs.
        - total_tickets
        - resolved_tickets
        - avg_resolution_time (duration)
        """

        # Treat unresolved tickets as NULL duration so they don't skew the avg
        resolution_duration = ExpressionWrapper(
            Case(
                When(
                    status="closed",
                    then=F("resolution_time") - F("created_at"),
                ),
                default=None,
                output_field=DurationField(),
            ),
            output_field=DurationField(),
        )

        stats = Ticket.objects.aggregate(
            total_tickets=Count("id"),
            resolved_tickets=Count("id", filter=Q(status="closed")),
            avg_resolution_time=Avg(resolution_duration),
        )

        # Serialize duration to seconds (or ISO 8601) for JSON-compat
        dur = stats["avg_resolution_time"]
        stats["avg_resolution_time_seconds"] = (
            dur.total_seconds() if dur is not None else None
        )
        # Keep the original value too (string like "1 day, 2:03:04")
        stats["avg_resolution_time"] = str(dur) if dur is not None else None

        return Response(stats, status=status.HTTP_200_OK)