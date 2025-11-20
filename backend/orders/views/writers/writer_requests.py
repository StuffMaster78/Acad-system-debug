from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from orders.models import WriterRequest, Order
from orders.serializers import WriterRequestSerializer
from orders.services.pricing_calculator import PricingCalculatorService 
from rest_framework import viewsets, status

from orders.permissions import IsClientWhoOwnsOrder, IsAuthenticated

class WriterRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling writer requests such as deadline extensions or page increases.
    """
    queryset = WriterRequest.objects.all()
    serializer_class = WriterRequestSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def submit_request(self, request, pk=None):
        """
        Submit a writer's request for changes to the order.
        """
        order = Order.objects.get(id=pk)
        request_type = request.data.get("request_type")
        reason = request.data.get("request_reason")

        if request_type == "deadline_extension":
            new_deadline = request.data.get("new_deadline")
            writer_request = WriterRequest.objects.create(
                order=order,
                request_type=request_type,
                requested_by_writer=request.user,
                new_deadline=new_deadline,
                request_reason=reason
            )
        elif request_type in ["page_increase", "slide_increase"]:
            additional_pages = request.data.get("additional_pages")
            additional_slides = request.data.get("additional_slides")
            writer_request = WriterRequest.objects.create(
                order=order,
                request_type=request_type,
                requested_by_writer=request.user,
                additional_pages=additional_pages,
                additional_slides=additional_slides,
                request_reason=reason
            )
        return Response({"message": "Writer request submitted successfully."}, status=201)

    @action(detail=True, methods=['post'])
    def approve_request(self, request, pk=None):
        """
        Approve or decline a writer's request for changes to the order.
        """
        order = self.get_object()
        writer_request_id = request.data.get("writer_request_id")
        writer_request = WriterRequest.objects.get(id=writer_request_id, order=order)

        client_response = request.data.get("response")

        if client_response == "approve":
            writer_request.status = "accepted"
            writer_request.save()

            # Handle payment for page/slide increase
            if writer_request.request_type in ["page_increase", "slide_increase"]:
                additional_cost = PricingCalculatorService.calculate_additional_cost(writer_request)
                payment = RequestPayment.objects.create(
                    order=order,
                    payment_method="wallet",  # Assuming wallet for now
                    additional_cost=additional_cost,
                    payment_for=writer_request.request_type
                )
                order.total_cost += additional_cost
                order.save()

            return Response({"message": "Request approved successfully."}, status=200)

        elif client_response == "decline":
            writer_request.status = "declined"
            writer_request.save()
            return Response({"message": "Request declined."}, status=200)

        return Response({"message": "Invalid response."}, status=400)