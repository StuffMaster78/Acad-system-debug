from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from orders.models import Order
from orders.serializers import DeadlineExtensionSerializer
from orders.services.order_deadline_service import OrderDeadlineService
from orders.permissions import IsOrderOwnerOrSupport


class ExtendOrderDeadlineView(APIView):
    """
    Allows the client (or support/admin) to extend the deadline of an order.

    Expects:
    # {
    #     "new_deadline": "2025-07-01T23:59:00Z"
    # }
    """
    permission_classes = [IsAuthenticated, IsOrderOwnerOrSupport]

    def post(self, request, pk):
        """
        Extend the deadline of an order.
        """
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Enforce object-level permission (owner/support)
        self.check_object_permissions(request, order)

        serializer = DeadlineExtensionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_deadline = serializer.validated_data['new_deadline']

        try:
            updated_order = OrderDeadlineService.update_deadline(
                order=order,
                new_deadline=new_deadline,
                actor=request.user,
                reason="Deadline extended by client or support"
            )
        except ValueError as ve:
            return Response(
                {"detail": str(ve)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": "Failed to extend deadline."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response({
            "status": "success",
            "order_id": updated_order.id,
            "new_deadline": getattr(updated_order, "client_deadline", None)
        }, status=status.HTTP_200_OK)