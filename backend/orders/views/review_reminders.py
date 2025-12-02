"""
ViewSets for Review Reminders
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from orders.models import ReviewReminder
from orders.serializers.review_reminders import ReviewReminderSerializer


class ReviewReminderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing review reminders.
    Read-only for users, admins can manage.
    """
    serializer_class = ReviewReminderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = ReviewReminder.objects.select_related(
            'order', 'client', 'writer'
        )
        
        if user.role == 'client':
            # Clients can only see their own reminders
            queryset = queryset.filter(client=user)
        elif user.role == 'writer':
            # Writers can see reminders for their orders
            queryset = queryset.filter(writer=user)
        elif user.is_staff or user.role in ['admin', 'superadmin', 'support']:
            # Staff can see all
            pass
        else:
            queryset = queryset.none()
        
        return queryset.filter(is_completed=False).order_by('-order_completed_at')
    
    @action(detail=True, methods=['post'], url_path='mark-reviewed')
    def mark_reviewed(self, request, pk=None):
        """Mark that client has submitted a review."""
        reminder = self.get_object()
        
        if reminder.client != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reminder.mark_as_reviewed()
        serializer = self.get_serializer(reminder)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='mark-rated')
    def mark_rated(self, request, pk=None):
        """Mark that client has rated the writer."""
        reminder = self.get_object()
        rating = request.data.get('rating')
        
        if reminder.client != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if rating and not (1 <= int(rating) <= 5):
            return Response(
                {'error': 'Rating must be between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reminder.mark_as_rated(rating=int(rating) if rating else None)
        serializer = self.get_serializer(reminder)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='my-reminders')
    def my_reminders(self, request):
        """Get current user's active review reminders."""
        if request.user.role == 'client':
            queryset = self.get_queryset().filter(client=request.user)
        elif request.user.role == 'writer':
            queryset = self.get_queryset().filter(writer=request.user)
        else:
            queryset = self.get_queryset()
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

