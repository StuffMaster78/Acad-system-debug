"""
Enhanced Revision Requests ViewSet
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from orders.enhanced_revisions import RevisionRequest
from orders.serializers.enhanced_revisions import (
    RevisionRequestSerializer,
    RevisionRequestCreateSerializer,
    RevisionRequestUpdateSerializer,
    RevisionRequestCompleteSerializer,
)


class RevisionRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing revision requests.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RevisionRequestSerializer
    
    def get_queryset(self):
        """Get revision requests based on user role."""
        user = self.request.user
        website = user.website
        
        if user.role == 'client':
            # Clients see their own revision requests
            queryset = RevisionRequest.objects.filter(
                requested_by=user,
                website=website
            )
        elif user.role in ['writer', 'editor']:
            # Writers/editors see assigned revisions
            queryset = RevisionRequest.objects.filter(
                Q(assigned_to=user) | Q(order__writer=user),
                website=website
            )
        else:
            # Admins/support see all
            queryset = RevisionRequest.objects.filter(website=website)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by severity
        severity_filter = self.request.query_params.get('severity')
        if severity_filter:
            queryset = queryset.filter(severity=severity_filter)
        
        # Filter by order
        order_id = self.request.query_params.get('order')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        return queryset.select_related(
            'order', 'requested_by', 'assigned_to', 'website'
        ).order_by('-priority', '-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return RevisionRequestCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return RevisionRequestUpdateSerializer
        return RevisionRequestSerializer
    
    def perform_create(self, serializer):
        """Create revision request."""
        serializer.save(
            requested_by=self.request.user,
            website=self.request.user.website
        )
        
        # Update order status
        order = serializer.instance.order
        if order.status in ['completed', 'approved']:
            order.status = 'revision_requested'
            order.save(update_fields=['status'])
    
    @action(detail=True, methods=['post'], url_path='complete')
    def complete_revision(self, request, pk=None):
        """Mark revision as completed."""
        revision = self.get_object()
        
        if not revision.can_complete():
            return Response(
                {'error': 'Revision cannot be completed in current state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = RevisionRequestCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Complete revision
            revision.complete(completed_by=request.user)
            
            # Add writer notes if provided
            if serializer.validated_data.get('writer_notes'):
                revision.writer_notes = serializer.validated_data['writer_notes']
                revision.save(update_fields=['writer_notes'])
            
            # Update order status
            if serializer.validated_data.get('mark_order_complete', False):
                revision.order.status = 'completed'
                revision.order.save(update_fields=['status'])
            else:
                revision.order.status = 'revision_in_progress'
                revision.order.save(update_fields=['status'])
            
            revision_serializer = self.get_serializer(revision)
            return Response({
                'message': 'Revision completed successfully',
                'revision': revision_serializer.data,
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to complete revision: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='assign')
    def assign_revision(self, request, pk=None):
        """Assign revision to writer/editor."""
        revision = self.get_object()
        assigned_to_id = request.data.get('assigned_to')
        
        if not assigned_to_id:
            return Response(
                {'error': 'assigned_to is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            assigned_to = User.objects.get(id=assigned_to_id)
            if assigned_to.role not in ['writer', 'editor']:
                return Response(
                    {'error': 'Can only assign to writers or editors'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            revision.assigned_to = assigned_to
            revision.status = 'in_progress'
            revision.save(update_fields=['assigned_to', 'status'])
            
            revision_serializer = self.get_serializer(revision)
            return Response({
                'message': 'Revision assigned successfully',
                'revision': revision_serializer.data,
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

