from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from models.payout import WriterPayment
from writer_management.services.payment_service  import WriterPaymentService
from decimal import Decimal
from writer_management.models.profile import WriterProfile
from websites.models import Website
from writer_management.serializers import WriterPaymentSerializer



class WriterPaymentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    def list(self, request):
        payments = WriterPayment.objects.select_related("writer", "website").order_by("-payment_date")
        serializer = WriterPaymentSerializer(payments, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            payment = WriterPayment.objects.get(pk=pk)
        except WriterPayment.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        serializer = WriterPaymentSerializer(payment)
        return Response(serializer.data)

    def create(self, request):
        data = request.data.copy()
        serializer = WriterPaymentSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        writer = serializer.validated_data["writer"]
        website = serializer.validated_data["website"]
        amount = serializer.validated_data["amount"]
        bonuses = serializer.validated_data.get("bonuses", Decimal("0.00"))
        fines = serializer.validated_data.get("fines", Decimal("0.00"))
        tips = serializer.validated_data.get("tips", Decimal("0.00"))
        currency = request.data.get("currency", "USD")
        convert = request.data.get("convert_to_local", False)

        payment = WriterPaymentService.create_payment(
            writer=writer,
            website=website,
            amount_usd=amount,
            bonuses=bonuses,
            fines=fines,
            tips=tips,
            currency=currency,
            convert_to_local=convert,
            description=serializer.validated_data.get("description", ""),
            actor=request.user
        )

        return Response(
            WriterPaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED
        )