"""
Streamlined views for special order management.
Provides unified endpoints for placing, negotiating, and completing orders.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from decimal import Decimal
from special_orders.models import SpecialOrder
from special_orders.serializers import SpecialOrderSerializer
from special_orders.services.streamlined_order_service import StreamlinedSpecialOrderService

logger = logging.getLogger(__name__)


class StreamlinedSpecialOrderViewSet(viewsets.ModelViewSet):
    """
    Streamlined ViewSet for special orders with unified workflow.
    """
    queryset = SpecialOrder.objects.select_related(
        'client', 'writer', 'predefined_type', 'website'
    ).prefetch_related('installments').order_by('-created_at')
    serializer_class = SpecialOrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = self.queryset
        
        if user.is_staff or getattr(user, 'role', None) in ['admin', 'superadmin', 'support']:
            return queryset
        elif getattr(user, 'role', None) == 'writer':
            return queryset.filter(writer=user)
        elif getattr(user, 'role', None) in ['client', 'customer']:
            return queryset.filter(client=user)
        
        return queryset.none()
    
    @action(detail=False, methods=['post'], url_path='place-order')
    def place_order(self, request):
        """
        Streamlined order placement endpoint.
        
        Request body:
        {
            "order_type": "predefined" | "estimated",
            "predefined_type_id": 123,  // If predefined
            "duration_days": 3,
            "inquiry_details": "Description",
            "website_id": 1,
            "price_per_day": 50.00  // Optional, for estimated
        }
        """
        try:
            order = StreamlinedSpecialOrderService.place_order(
                data=request.data,
                client=request.user
            )
            serializer = SpecialOrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception(f"Error placing order: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser], url_path='set-price')
    def set_price(self, request, pk=None):
        """
        Set or negotiate price for an estimated order (admin).
        Can be called multiple times for negotiation.
        
        Request body:
        {
            "total_cost": 500.00,  // Optional
            "price_per_day": 50.00,  // Optional
            "admin_notes": "Negotiated price based on complexity"
        }
        """
        order = self.get_object()
        
        try:
            updated_order = StreamlinedSpecialOrderService.set_price(
                order=order,
                admin_user=request.user,
                total_cost=request.data.get('total_cost'),
                price_per_day=request.data.get('price_per_day'),
                admin_notes=request.data.get('admin_notes')
            )
            serializer = SpecialOrderSerializer(updated_order)
            return Response(serializer.data)
        except Exception as e:
            logger.exception(f"Error setting price: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser], url_path='approve-and-assign')
    def approve_and_assign(self, request, pk=None):
        """
        Streamlined approval and writer assignment in one action.
        
        Request body:
        {
            "writer_id": 123,  // Optional
            "writer_payment_amount": 100.00,  // Optional
            "writer_payment_percentage": 15.5,  // Optional
            "auto_assign": false  // Optional, auto-assign best writer
        }
        """
        order = self.get_object()
        
        try:
            result = StreamlinedSpecialOrderService.approve_and_assign(
                order=order,
                admin_user=request.user,
                writer_id=request.data.get('writer_id'),
                writer_payment_amount=request.data.get('writer_payment_amount'),
                writer_payment_percentage=request.data.get('writer_payment_percentage'),
                auto_assign=request.data.get('auto_assign', False)
            )
            serializer = SpecialOrderSerializer(result['order'])
            return Response({
                'order': serializer.data,
                'writer_assigned': result['writer_assigned'],
                'status': result['status'],
            })
        except Exception as e:
            logger.exception(f"Error approving and assigning: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='complete')
    def complete_order(self, request, pk=None):
        """
        Streamlined order completion.
        
        Request body:
        {
            "files_uploaded": true,  // Optional, default true
            "completion_notes": "Order completed successfully"  // Optional
        }
        """
        order = self.get_object()
        
        try:
            completed_order = StreamlinedSpecialOrderService.complete_order(
                order=order,
                completed_by=request.user,
                files_uploaded=request.data.get('files_uploaded', True),
                completion_notes=request.data.get('completion_notes')
            )
            serializer = SpecialOrderSerializer(completed_order)
            return Response(serializer.data)
        except Exception as e:
            logger.exception(f"Error completing order: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'], url_path='workflow-status')
    def workflow_status(self, request, pk=None):
        """
        Get current workflow status and available actions.
        """
        order = self.get_object()
        status_info = StreamlinedSpecialOrderService.get_order_workflow_status(
            order=order,
            user=request.user
        )
        return Response(status_info)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser], url_path='quick-approve')
    def quick_approve(self, request, pk=None):
        """
        Quick approve: Set price, approve, and assign writer in one action.
        
        Request body:
        {
            "total_cost": 500.00,  // Required for estimated orders
            "price_per_day": 50.00,  // Optional alternative
            "writer_id": 123,  // Optional
            "writer_payment_amount": 100.00,  // Optional
            "writer_payment_percentage": 15.5,  // Optional
            "admin_notes": "Quick approval"  // Optional
        }
        """
        order = self.get_object()
        
        try:
            # Set price if estimated and price provided
            if order.order_type == 'estimated' and (request.data.get('total_cost') or request.data.get('price_per_day')):
                order = StreamlinedSpecialOrderService.set_price(
                    order=order,
                    admin_user=request.user,
                    total_cost=request.data.get('total_cost'),
                    price_per_day=request.data.get('price_per_day'),
                    admin_notes=request.data.get('admin_notes')
                )
            
            # Approve and assign
            result = StreamlinedSpecialOrderService.approve_and_assign(
                order=order,
                admin_user=request.user,
                writer_id=request.data.get('writer_id'),
                writer_payment_amount=request.data.get('writer_payment_amount'),
                writer_payment_percentage=request.data.get('writer_payment_percentage'),
                auto_assign=request.data.get('auto_assign', False)
            )
            
            serializer = SpecialOrderSerializer(result['order'])
            return Response({
                'order': serializer.data,
                'writer_assigned': result['writer_assigned'],
                'status': result['status'],
                'message': 'Order approved and ready for work'
            })
        except Exception as e:
            logger.exception(f"Error in quick approve: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

