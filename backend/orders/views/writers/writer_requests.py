from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from decimal import Decimal

from orders.models import WriterRequest, Order
from orders.serializers import WriterRequestSerializer
from orders.services.writer_request_service import WriterRequestService
from orders.permissions import IsClientWhoOwnsOrder
from order_payments_management.services.unified_payment_service import UnifiedPaymentService


class WriterRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling writer requests such as deadline extensions or page increases.
    """
    queryset = WriterRequest.objects.select_related('order', 'requested_by_writer', 'website').all()
    serializer_class = WriterRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter requests based on user role."""
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.role == 'writer':
            # Writers see their own requests
            return queryset.filter(requested_by_writer=user)
        elif user.role == 'client':
            # Clients see requests for their orders
            return queryset.filter(order__client=user)
        elif user.role in ['admin', 'superadmin', 'support']:
            # Admins see all requests
            return queryset
        
        return queryset.none()

    @action(detail=False, methods=['post'], url_path='create')
    def create_request(self, request):
        """
        Create a new writer request for page/slide increase or deadline extension.
        
        Expected payload:
        {
            "order_id": int,
            "request_type": "page_increase" | "slide_increase" | "deadline_extension",
            "request_reason": str,
            "additional_pages": int (optional, for page_increase),
            "additional_slides": int (optional, for slide_increase),
            "new_deadline": str (optional, for deadline_extension)
        }
        """
        if request.user.role != 'writer':
            return Response(
                {"detail": "Only writers can create requests."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        order_id = request.data.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        
        # Verify writer is assigned to this order
        if order.assigned_writer != request.user:
            return Response(
                {"detail": "You are not assigned to this order."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        request_type = request.data.get('request_type')
        request_reason = request.data.get('request_reason')
        
        if not request_reason:
            return Response(
                {"detail": "request_reason is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = {}
        if request_type == WriterRequest.RequestType.DEADLINE:
            new_deadline = request.data.get('new_deadline')
            if not new_deadline:
                return Response(
                    {"detail": "new_deadline is required for deadline extension."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data['new_deadline'] = new_deadline
        elif request_type == WriterRequest.RequestType.PAGES:
            additional_pages = request.data.get('additional_pages')
            if not additional_pages or additional_pages <= 0:
                return Response(
                    {"detail": "additional_pages must be a positive integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data['additional_pages'] = additional_pages
        elif request_type == WriterRequest.RequestType.SLIDES:
            additional_slides = request.data.get('additional_slides')
            if not additional_slides or additional_slides <= 0:
                return Response(
                    {"detail": "additional_slides must be a positive integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data['additional_slides'] = additional_slides
        else:
            return Response(
                {"detail": "Invalid request_type."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            writer_request = WriterRequestService.create_request(
                order=order,
                writer=request.user,
                request_type=request_type,
                reason=request_reason,
                data=data
            )
            
            serializer = self.get_serializer(writer_request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], url_path='client-respond')
    def client_respond(self, request, pk=None):
        """
        Client responds to a writer request: accept, decline, or counteroffer.
        
        Expected payload:
        {
            "action": "accept" | "decline" | "counteroffer",
            "counter_pages": int (optional, for counteroffer),
            "counter_slides": int (optional, for counteroffer),
            "counter_cost": decimal (optional, for counteroffer),
            "counter_reason": str (required for counteroffer),
            "reason": str (optional, for decline)
        }
        """
        writer_request = get_object_or_404(WriterRequest, pk=pk)
        
        # Verify client owns the order
        if writer_request.order.client != request.user:
            return Response(
                {"detail": "You do not have permission to respond to this request."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if writer_request.status != WriterRequest.RequestStatus.PENDING:
            return Response(
                {"detail": "This request has already been handled."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        action_type = request.data.get('action')
        
        try:
            if action_type == 'accept':
                WriterRequestService.client_respond(
                    request=writer_request,
                    client=request.user,
                    approve=True
                )
                
                # If payment is required, return payment info
                if writer_request.requires_payment:
                    return Response({
                        "message": "Request accepted. Payment required.",
                        "writer_request": self.get_serializer(writer_request).data,
                        "requires_payment": True,
                        "amount": str(writer_request.final_cost),
                        "payment_url": f"/orders/{writer_request.order.id}/pay-writer-request/{writer_request.id}"
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "message": "Request accepted successfully.",
                        "writer_request": self.get_serializer(writer_request).data
                    }, status=status.HTTP_200_OK)
                    
            elif action_type == 'decline':
                reason = request.data.get('reason', '')
                WriterRequestService.client_respond(
                    request=writer_request,
                    client=request.user,
                    approve=False,
                    reason=reason
                )
                return Response({
                    "message": "Request declined.",
                    "writer_request": self.get_serializer(writer_request).data
                }, status=status.HTTP_200_OK)
                
            elif action_type == 'counteroffer':
                counter_offer_data = {
                    'counter_pages': request.data.get('counter_pages'),
                    'counter_slides': request.data.get('counter_slides'),
                    'counter_cost': request.data.get('counter_cost'),
                    'counter_reason': request.data.get('counter_reason')
                }
                
                if not counter_offer_data.get('counter_reason'):
                    return Response(
                        {"detail": "counter_reason is required for counteroffer."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                WriterRequestService.client_respond(
                    request=writer_request,
                    client=request.user,
                    approve=False,
                    counter_offer_data=counter_offer_data
                )
                return Response({
                    "message": "Counter offer submitted.",
                    "writer_request": self.get_serializer(writer_request).data
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "Invalid action. Must be 'accept', 'decline', or 'counteroffer'."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'], url_path='pricing-preview')
    def pricing_preview(self, request, pk=None):
        """
        Get pricing preview for a writer request before creating it.
        """
        order_id = request.query_params.get('order_id')
        request_type = request.query_params.get('request_type')
        additional_pages = request.query_params.get('additional_pages', 0)
        additional_slides = request.query_params.get('additional_slides', 0)
        
        if not order_id or not request_type:
            return Response(
                {"detail": "order_id and request_type are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order = get_object_or_404(Order, id=order_id)
        
        # Create a temporary request to calculate pricing
        temp_request = WriterRequest(
            order=order,
            website=order.website,
            request_type=request_type,
            additional_pages=int(additional_pages) if additional_pages else None,
            additional_slides=int(additional_slides) if additional_slides else None
        )
        
        from orders.services.writer_request_pricing_service import WriterRequestPricingService
        pricing_service = WriterRequestPricingService(temp_request)
        pricing_service.update_writer_request_costs(save=False)
        
        return Response({
            "estimated_cost": str(temp_request.estimated_cost or Decimal('0.00')),
            "final_cost": str(temp_request.final_cost or Decimal('0.00')),
            "requires_payment": bool(temp_request.final_cost and temp_request.final_cost > 0),
            "breakdown": pricing_service.get_breakdown() if hasattr(pricing_service, 'get_breakdown') else {}
        }, status=status.HTTP_200_OK)