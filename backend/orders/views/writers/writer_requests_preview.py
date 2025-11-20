# orders/views/writer_request_preview.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from orders.models import Order
from orders.serializers import WriterRequestPreviewSerializer
from orders.models import WriterRequest
from orders.services.writer_request_pricing_service import WriterRequestPricingService


class WriterRequestPreviewView(APIView):
    """
    Public endpoint to preview the cost of a writer request
    (like adding pages/slides) before submission.
    """

    def post(self, request):
        serializer = WriterRequestPreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data
        try:
            order = Order.objects.get(id=validated["order_id"])
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=404)

        # Create a temporary request object in memory (not saved)
        temp_request = WriterRequest(
            order=order,
            website=order.website,
            request_type=validated["request_type"],
            additional_pages=validated.get("additional_pages", 0),
            additional_slides=validated.get("additional_slides", 0),
        )

        pricing_service = WriterRequestPricingService(temp_request)
        estimate = pricing_service.calculate_estimated_cost()
        final = pricing_service.calculate_discounted_cost()

        return Response({
            "estimated_cost": str(estimate),
            "final_cost_after_discount": str(final),
            "discount_applied": order.discount.code if order.discount else None
        })
