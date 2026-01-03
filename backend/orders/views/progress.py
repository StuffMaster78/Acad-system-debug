"""
Views for writer progress reports.
"""
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Max
from django.utils import timezone

from orders.models import WriterProgress, Order
from orders.serializers.progress import WriterProgressSerializer, WriterProgressListSerializer
from authentication.permissions import IsAdmin, IsSuperadminOrAdmin


class WriterProgressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing writer progress reports.
    """
    queryset = WriterProgress.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return WriterProgressListSerializer
        return WriterProgressSerializer
    
    def get_queryset(self):
        """Filter progress reports based on user role."""
        user = self.request.user
        user_role = getattr(user, 'role', None)
        
        queryset = WriterProgress.objects.select_related(
            'writer', 'order', 'withdrawn_by', 'website'
        )
        
        # Writers can only see their own progress reports
        if user_role == 'writer':
            queryset = queryset.filter(writer=user)
        # Clients can see progress for their orders
        elif user_role == 'client':
            queryset = queryset.filter(order__client=user)
        # Admins/superadmins can see all
        elif user_role not in ['admin', 'superadmin', 'support']:
            queryset = queryset.none()
        
        # Filter by order if provided
        order_id = self.request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        # Filter out withdrawn reports for non-admins
        if user_role not in ['admin', 'superadmin', 'support']:
            queryset = queryset.filter(is_withdrawn=False)
        
        return queryset.order_by('-timestamp')
    
    def perform_create(self, serializer):
        """Create a progress report."""
        user = self.request.user
        user_role = getattr(user, 'role', None)
        
        # Only writers can create progress reports
        if user_role != 'writer':
            raise serializers.ValidationError("Only writers can create progress reports.")
        
        # Validate that the writer is assigned to the order
        order = serializer.validated_data.get('order')
        if order and order.assigned_writer != user:
            raise serializers.ValidationError("You can only report progress for orders assigned to you.")
        
        serializer.save()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsSuperadminOrAdmin])
    def withdraw(self, request, pk=None):
        """
        Withdraw a progress report (admin/superadmin only).
        Used when screened words are detected or policy violations occur.
        """
        progress = self.get_object()
        
        if progress.is_withdrawn:
            return Response(
                {'error': 'This progress report is already withdrawn.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', 'Policy violation detected')
        progress.withdraw(withdrawn_by=request.user, reason=reason)
        
        serializer = self.get_serializer(progress)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='order/(?P<order_id>[^/.]+)/latest')
    def get_latest_progress(self, request, order_id=None):
        """Get the latest progress report for an order."""
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        user = request.user
        user_role = getattr(user, 'role', None)
        
        if user_role == 'writer' and order.assigned_writer != user:
            # Check if writer has requested this order
            from writer_management.models.requests import WriterOrderRequest
            try:
                writer_profile = user.writer_profile
                has_requested = WriterOrderRequest.objects.filter(
                    writer=writer_profile,
                    order=order
                ).exists()
                if not has_requested:
                    return Response(
                        {'error': 'You can only view progress for your assigned orders or orders you have requested.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Exception:
                return Response(
                    {'error': 'You can only view progress for your assigned orders.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif user_role == 'client' and order.client != user:
            return Response(
                {'error': 'You can only view progress for your orders.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        latest = WriterProgress.objects.filter(
            order=order,
            is_withdrawn=False
        ).order_by('-timestamp').first()
        
        if not latest:
            return Response({'progress_percentage': 0, 'latest_report': None})
        
        serializer = WriterProgressSerializer(latest, context={'request': request})
        return Response({
            'progress_percentage': latest.progress_percentage,
            'latest_report': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='order/(?P<order_id>[^/.]+)/history')
    def get_progress_history(self, request, order_id=None):
        """Get all progress reports for an order."""
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        user = request.user
        user_role = getattr(user, 'role', None)
        
        if user_role == 'writer' and order.assigned_writer != user:
            return Response(
                {'error': 'You can only view progress for your assigned orders.'},
                status=status.HTTP_403_FORBIDDEN
            )
        elif user_role == 'client' and order.client != user:
            return Response(
                {'error': 'You can only view progress for your orders.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = WriterProgress.objects.filter(order=order)
        
        # Admins can see withdrawn reports
        if user_role not in ['admin', 'superadmin', 'support']:
            queryset = queryset.filter(is_withdrawn=False)
        
        progress_reports = queryset.order_by('-timestamp')
        serializer = WriterProgressListSerializer(progress_reports, many=True, context={'request': request})
        
        return Response({
            'order_id': order_id,
            'total_reports': progress_reports.count(),
            'reports': serializer.data
        })

