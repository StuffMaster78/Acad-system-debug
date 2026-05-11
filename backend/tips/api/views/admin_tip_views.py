# tips/api/views/admin_tip_views.py

from django.shortcuts import get_object_or_404
from typing import Any
from rest_framework import status
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from tips.models.tip import Tip

from tips.api.serializers.tip_detail_serializers import (
    TipDetailSerializer,
)

from tips.selectors.tip_selectors import (
    get_tip_by_id,
)

from tips.services.tip_retry_service import (
    TipRetryService,
)

from tips.services.tip_cancel_service import (
    TipCancelService,
)

from tips.services.tip_failure_service import (
    TipFailureService,
)


class AdminTipListAPIView(ListAPIView):
    """
    Full admin tip listing endpoint.
    """

    permission_classes = [IsAdminUser]
    serializer_class = TipDetailSerializer

    queryset = (
        Tip.objects
        .select_related(
            "sender",
            "receiver",
            "payment_intent",
            "active_policy",
        )
        .order_by("-created_at")
    )


class AdminTipDetailAPIView(RetrieveAPIView):
    """
    Full admin tip detail.
    """

    permission_classes = [IsAdminUser]
    serializer_class = TipDetailSerializer
    lookup_field = "pk"

    queryset = (
        Tip.objects
        .select_related(
            "sender",
            "receiver",
            "payment_intent",
            "active_policy",
        )
    )

    def get_object(self) -> Any:
        return get_tip_by_id(
            tip_id=self.kwargs["pk"],
        )


class AdminRetryTipAPIView(APIView):
    """
    Retry failed/pending tip processing.
    """

    permission_classes = [IsAdminUser]

    def post(self, request, pk):

        tip = get_object_or_404(Tip, pk=pk)

        retried_tip = TipRetryService.retry(
            tip=tip,
            triggered_by=request.user,
        )

        return Response(
            TipDetailSerializer(retried_tip).data,
            status=status.HTTP_200_OK,
        )


class AdminCancelTipAPIView(APIView):
    """
    Cancel pending tip.
    """

    permission_classes = [IsAdminUser]

    def post(self, request, pk):

        tip = get_object_or_404(Tip, pk=pk)

        cancelled_tip = TipCancelService.cancel(
            tip=tip,
            triggered_by=request.user,
        )

        return Response(
            TipDetailSerializer(cancelled_tip).data,
            status=status.HTTP_200_OK,
        )


class AdminFailTipAPIView(APIView):
    """
    Force mark a tip as failed.
    """

    permission_classes = [IsAdminUser]

    def post(self, request, pk):

        tip = get_object_or_404(Tip, pk=pk)

        failed_tip = TipFailureService.fail(
            tip=tip,
            triggered_by=request.user,
        )

        return Response(
            TipDetailSerializer(failed_tip).data,
            status=status.HTTP_200_OK,
        )