"""
ViewSet for preferred writers to accept or reject order assignments.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from orders.models import Order
from orders.services.preferred_writer_response import PreferredWriterResponseService
from orders.serializers import OrderSerializer


class PreferredWriterResponseViewSet(viewsets.ViewSet):
    """
    ViewSet for preferred writers to accept or reject order assignments.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='pending')
    def pending_assignments(self, request):
        """
        Get all pending preferred writer assignments for the current writer.
        """
        user = request.user
        if user.role != 'writer':
            return Response(
                {"error": "Only writers can view pending preferred assignments."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get orders where this writer is the preferred writer and status is pending_preferred
        pending_orders = Order.objects.filter(
            preferred_writer=user,
            status='pending_preferred'
        ).select_related(
            'client', 'type_of_work', 'paper_type', 'subject', 'website'
        ).order_by('-created_at')
        
        data = []
        for order in pending_orders:
            data.append({
                'order_id': order.id,
                'order': OrderSerializer(order).data,
                'created_at': order.created_at,
            })
        
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='(?P<order_id>[^/.]+)/accept/')
    def accept_assignment(self, request, order_id=None):
        """
        Preferred writer accepts the assignment.
        Moves order to 'in_progress' status and assigns the writer.
        """
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify the writer is the preferred writer
        if order.preferred_writer != request.user:
            return Response(
                {"error": "You are not the preferred writer for this order."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if order.status != 'pending_preferred':
            return Response(
                {"error": f"Order is not pending preferred writer response. Current status: {order.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            updated_order = PreferredWriterResponseService.accept(order_id, request.user)
            
            from orders.notification_emitters import emit_event
            emit_event(
                "order.preferred_writer_accepted",
                order=order,
                actor=request.user,
                extra={"order_id": order.id}
            )
            
            return Response(
                {
                    "message": "Assignment accepted successfully",
                    "order_id": updated_order.id,
                    "status": "accepted",
                    "order": OrderSerializer(updated_order).data
                },
                status=status.HTTP_200_OK
            )
        except (ObjectDoesNotExist, ValueError) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to accept assignment: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='(?P<order_id>[^/.]+)/reject/')
    def reject_assignment(self, request, order_id=None):
        """
        Preferred writer rejects the assignment.
        Returns order to 'available' status and clears preferred writer.
        """
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify the writer is the preferred writer
        if order.preferred_writer != request.user:
            return Response(
                {"error": "You are not the preferred writer for this order."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if order.status != 'pending_preferred':
            return Response(
                {"error": f"Order is not pending preferred writer response. Current status: {order.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        
        try:
            updated_order = PreferredWriterResponseService.reject(order_id, request.user, reason=reason)
            
            from orders.notification_emitters import emit_event

            emit_event(
                "order.preferred_writer_rejected",
                order=order,
                actor=request.user,
                extra={"reason": reason, "order_id": order.id}
            )
            
            return Response(
                {
                    "message": "Assignment rejected. Order returned to available pool.",
                    "order_id": updated_order.id,
                    "status": "rejected",
                    "order": OrderSerializer(updated_order).data
                },
                status=status.HTTP_200_OK
            )
        except (ObjectDoesNotExist, ValueError) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to reject assignment: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

