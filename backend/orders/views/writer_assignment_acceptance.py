"""
ViewSet for writers to accept or reject order assignments.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from orders.models import Order, WriterAssignmentAcceptance
from orders.permissions import IsAssignedWriter


class WriterAssignmentAcceptanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for writers to accept or reject order assignments.
    """
    queryset = WriterAssignmentAcceptance.objects.select_related(
        'order', 'writer', 'assigned_by', 'website'
    ).all()
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Writers can only see their own assignment acceptances."""
        user = self.request.user
        if user.role in ['admin', 'superadmin', 'support']:
            return self.queryset
        return self.queryset.filter(writer=user)
    
    @action(detail=True, methods=['post'], url_path='accept')
    def accept_assignment(self, request, pk=None):
        """
        Writer accepts the assignment.
        Moves order to 'in_progress' status.
        """
        acceptance = self.get_object()
        
        # Verify the writer is the one assigned
        if acceptance.writer != request.user:
            return Response(
                {"error": "You are not assigned to this order."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if acceptance.status != 'pending':
            return Response(
                {"error": f"Assignment is already {acceptance.get_status_display()}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        
        try:
            acceptance.accept(reason=reason)
            return Response(
                {
                    "message": "Assignment accepted successfully",
                    "order_id": acceptance.order.id,
                    "status": "accepted"
                },
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='reject')
    def reject_assignment(self, request, pk=None):
        """
        Writer rejects the assignment.
        Returns order to 'available' status and unassigns writer.
        """
        acceptance = self.get_object()
        
        # Verify the writer is the one assigned
        if acceptance.writer != request.user:
            return Response(
                {"error": "You are not assigned to this order."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if acceptance.status != 'pending':
            return Response(
                {"error": f"Assignment is already {acceptance.get_status_display()}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        
        try:
            acceptance.reject(reason=reason)
            return Response(
                {
                    "message": "Assignment rejected. Order returned to available pool.",
                    "order_id": acceptance.order.id,
                    "status": "rejected"
                },
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='pending')
    def pending_assignments(self, request):
        """
        Get all pending assignments for the current writer.
        """
        user = request.user
        if user.role != 'writer':
            return Response(
                {"error": "Only writers can view pending assignments."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        pending = self.queryset.filter(
            writer=user,
            status='pending'
        ).order_by('-assigned_at')
        
        from orders.serializers import OrderSerializer
        data = []
        for acceptance in pending:
            data.append({
                'id': acceptance.id,
                'order_id': acceptance.order.id,
                'order': OrderSerializer(acceptance.order).data,
                'assigned_at': acceptance.assigned_at,
                'assigned_by': acceptance.assigned_by.username if acceptance.assigned_by else None,
            })
        
        return Response(data, status=status.HTTP_200_OK)

