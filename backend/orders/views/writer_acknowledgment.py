"""
ViewSets for Writer Assignment Acknowledgment
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from orders.models import Order, WriterAssignmentAcknowledgment
from orders.serializers.writer_acknowledgment import WriterAssignmentAcknowledgmentSerializer


class WriterAssignmentAcknowledgmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing writer assignment acknowledgments.
    """
    serializer_class = WriterAssignmentAcknowledgmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = WriterAssignmentAcknowledgment.objects.select_related(
            'order', 'writer'
        )
        
        if user.role == 'writer':
            # Writers can only see their own acknowledgments
            queryset = queryset.filter(writer=user)
        elif user.role == 'client':
            # Clients can see acknowledgments for their orders
            queryset = queryset.filter(order__client=user)
        elif user.is_staff or user.role in ['admin', 'superadmin', 'support']:
            # Staff can see all
            pass
        else:
            queryset = queryset.none()
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['post'], url_path='acknowledge/(?P<order_id>[^/.]+)')
    def acknowledge(self, request, order_id=None):
        """Writer acknowledges assignment to an order."""
        if request.user.role != 'writer':
            return Response(
                {'error': 'Only writers can acknowledge assignments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        order = get_object_or_404(Order, id=order_id)
        
        if order.assigned_writer != request.user:
            return Response(
                {'error': 'You are not assigned to this order'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        acknowledgment, created = WriterAssignmentAcknowledgment.objects.get_or_create(
            order=order,
            writer=request.user,
            defaults={}
        )
        
        if not created:
            acknowledgment.acknowledge()
        
        serializer = self.get_serializer(acknowledgment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='mark-message-sent')
    def mark_message_sent(self, request, pk=None):
        """Mark that writer has sent a message to client."""
        acknowledgment = self.get_object()
        
        if acknowledgment.writer != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        acknowledgment.mark_message_sent()
        serializer = self.get_serializer(acknowledgment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='mark-file-downloaded')
    def mark_file_downloaded(self, request, pk=None):
        """Mark that writer has downloaded order files."""
        acknowledgment = self.get_object()
        
        if acknowledgment.writer != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        acknowledgment.mark_file_downloaded()
        serializer = self.get_serializer(acknowledgment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='my-acknowledgments')
    def my_acknowledgments(self, request):
        """Get current user's acknowledgments."""
        if request.user.role != 'writer':
            return Response(
                {'error': 'Only writers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset().filter(writer=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

