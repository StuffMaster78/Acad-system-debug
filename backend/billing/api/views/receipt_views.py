from __future__ import annotations

from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.api.permissions.payment_permissions import CanViewPayments
from billing.api.serializers.receipt_serializers import (
    ReceiptReadSerializer,
)
from billing.models.receipt import Receipt
from billing.selectors.receipt_selectors import ReceiptSelector
from core.utils.request_context import get_request_website


class ReceiptListView(APIView):
    """
    List receipts for the resolved tenant.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanViewPayments,
    ]

    def get(self, request: Request) -> Response:
        website = get_request_website(request)

        queryset = ReceiptSelector.get_queryset_for_website(
            website=website,
        ).order_by("-issued_at", "-created_at")

        serializer = ReceiptReadSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReceiptDetailView(APIView):
    """
    Retrieve a single receipt for the resolved tenant.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanViewPayments,
    ]

    @staticmethod
    def _get_receipt(*, website: Any, receipt_id: int) -> Receipt:
        queryset = ReceiptSelector.get_queryset_for_website(
            website=website,
        )
        return get_object_or_404(
            queryset,
            pk=receipt_id,
        )

    def get(self, request: Request, receipt_id: int) -> Response:
        website = get_request_website(request)

        receipt = self._get_receipt(
            website=website,
            receipt_id=receipt_id,
        )

        serializer = ReceiptReadSerializer(receipt)
        return Response(serializer.data, status=status.HTTP_200_OK)