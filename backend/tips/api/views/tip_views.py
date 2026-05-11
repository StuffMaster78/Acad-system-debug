from django.contrib.auth import get_user_model
from django.db import transaction
from typing import cast

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from tips.api.serializers.tip_serializers import CreateTipSerializer
from tips.api.serializers.tip_detail_serializers import TipDetailSerializer

from tips.contracts.tip_creation_contract import TipCreationContract
from tips.services.tip_creation_service import TipCreationService

from tips.models.tip import Tip
from tips.selectors.tip_selectors import (
    get_tips_sent_by_user,
    get_tips_received_by_user,
    get_tip_by_id,
)

from tips.api.permissions.permissions import IsTipParticipant


User = get_user_model()


class CreateTipView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CreateTipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        sender = request.user
        receiver = User.objects.get(id=data["receiver_id"])

        contract = TipCreationContract(
            sender=sender,
            receiver=receiver,
            gross_amount=data["gross_amount_cents"],
            source_type="api",
            idempotency_key=data["idempotency_key"],
            reason=data.get("reason", ""),
            currency=data.get("currency", "USD"),
            context_type=data.get("context_type", ""),
            order_id=None,
            special_order_id=None,
            class_purchase_id=None,
        )

        tip = TipCreationService.create(contract)

        return Response(
            TipDetailSerializer(tip).data,
            status=status.HTTP_201_CREATED,
        )


class SentTipsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TipDetailSerializer

    def get_queryset(self): # type: ignore[override]
        user = self.request.user
        assert user.pk is not None
        return get_tips_sent_by_user(user_id=user.pk)


class ReceivedTipsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TipDetailSerializer

    def get_queryset(self): # type: ignore[override]
        user = self.request.user
        assert user.pk is not None
        return get_tips_received_by_user(user_id=user.pk)


class TipDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsTipParticipant]
    serializer_class = TipDetailSerializer

    def get_queryset(self): # type: ignore[override]
        return Tip.objects.all()