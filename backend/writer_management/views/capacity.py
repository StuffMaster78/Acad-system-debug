"""
Writer Capacity & Editor Workload ViewSets
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from writer_management.models.capacity import WriterCapacity, EditorWorkload
from writer_management.serializers.capacity import (
    WriterCapacitySerializer,
    WriterCapacityUpdateSerializer,
    EditorWorkloadSerializer,
)


class WriterCapacityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing writer capacity settings.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = WriterCapacitySerializer
    
    def get_queryset(self):
        """Get capacity settings for current user."""
        if self.request.user.role != 'writer':
            return WriterCapacity.objects.none()
        
        return WriterCapacity.objects.filter(
            writer=self.request.user,
            website=self.request.user.website
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['update', 'partial_update']:
            return WriterCapacityUpdateSerializer
        return WriterCapacitySerializer
    
    def perform_create(self, serializer):
        """Create capacity settings for current user."""
        serializer.save(
            writer=self.request.user,
            website=self.request.user.website
        )
    
    @action(detail=False, methods=['get'], url_path='my-capacity')
    def my_capacity(self, request):
        """Get current user's capacity settings."""
        try:
            capacity = WriterCapacity.objects.get(
                writer=request.user,
                website=request.user.website
            )
            serializer = self.get_serializer(capacity)
            return Response(serializer.data)
        except WriterCapacity.DoesNotExist:
            # Return defaults
            return Response({
                'max_active_orders': 5,
                'current_active_orders': 0,
                'is_available': True,
                'availability_message': '',
                'preferred_deadline_buffer_days': 3,
            })
    
    @action(detail=False, methods=['post'], url_path='update-active-count')
    def update_active_count(self, request):
        """Manually update active orders count."""
        try:
            capacity = WriterCapacity.objects.get(
                writer=request.user,
                website=request.user.website
            )
            capacity.update_active_orders_count()
            serializer = self.get_serializer(capacity)
            return Response(serializer.data)
        except WriterCapacity.DoesNotExist:
            return Response(
                {'error': 'Capacity settings not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], url_path='add-blackout')
    def add_blackout(self, request, pk=None):
        """Add a blackout period."""
        capacity = self.get_object()
        
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        reason = request.data.get('reason', '')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.utils.dateparse import parse_date
        try:
            start = parse_date(start_date)
            end = parse_date(end_date)
            
            if not start or not end:
                raise ValueError("Invalid date format")
            
            capacity.add_blackout_period(start, end, reason)
            
            serializer = self.get_serializer(capacity)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Failed to add blackout: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class EditorWorkloadViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing editor workload settings.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EditorWorkloadSerializer
    
    def get_queryset(self):
        """Get workload settings for current user."""
        if self.request.user.role != 'editor':
            return EditorWorkload.objects.none()
        
        return EditorWorkload.objects.filter(
            editor=self.request.user,
            website=self.request.user.website
        )
    
    def perform_create(self, serializer):
        """Create workload settings for current user."""
        serializer.save(
            editor=self.request.user,
            website=self.request.user.website
        )
    
    @action(detail=False, methods=['get'], url_path='my-workload')
    def my_workload(self, request):
        """Get current user's workload settings."""
        try:
            workload = EditorWorkload.objects.get(
                editor=request.user,
                website=request.user.website
            )
            serializer = self.get_serializer(workload)
            return Response(serializer.data)
        except EditorWorkload.DoesNotExist:
            # Return defaults
            return Response({
                'max_active_tasks': 10,
                'current_active_tasks': 0,
                'is_available': True,
            })

