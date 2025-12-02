"""
ViewSets for Message Reminders
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from orders.models import MessageReminder
from orders.serializers.message_reminders import MessageReminderSerializer


class MessageReminderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing message reminders.
    Read-only for users, admins can manage.
    """
    serializer_class = MessageReminderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = MessageReminder.objects.select_related(
            'order', 'user', 'message'
        )
        
        if user.role in ['writer', 'client']:
            # Users can only see their own reminders
            queryset = queryset.filter(user=user)
        elif user.is_staff or user.role in ['admin', 'superadmin', 'support']:
            # Staff can see all
            pass
        else:
            queryset = queryset.none()
        
        return queryset.filter(is_resolved=False).order_by('-created_at')
    
    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """Mark message as read."""
        reminder = self.get_object()
        
        if reminder.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reminder.mark_as_read()
        serializer = self.get_serializer(reminder)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='mark-responded')
    def mark_responded(self, request, pk=None):
        """Mark message as responded."""
        reminder = self.get_object()
        
        if reminder.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reminder.mark_as_responded()
        serializer = self.get_serializer(reminder)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='my-reminders')
    def my_reminders(self, request):
        """Get current user's active reminders."""
        queryset = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

