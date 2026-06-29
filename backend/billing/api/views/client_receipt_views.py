from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.api.serializers.receipt_serializers import ReceiptReadSerializer
from billing.selectors.receipt_selectors import ReceiptSelector
from core.utils.request_context import get_request_website


class ClientReceiptListView(APIView):
    """
    List receipts belonging to the authenticated client within the
    current tenant, ordered most-recent first.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        website = get_request_website(request)
        queryset = ReceiptSelector.get_queryset_for_client(
            website=website,
            client=request.user,
        ).order_by("-issued_at", "-created_at")

        serializer = ReceiptReadSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
