from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.api.serializers.payment_request_summary_serializers import (
    PaymentRequestSummarySerializer,
)
from billing.api.permissions.payment_permissions import (
    CanViewOwnPayments,
)
from billing.models.payment_request import PaymentRequest
from billing.selectors.payment_request_selectors import (
    PaymentRequestSelector,
)
from core.utils.request_context import get_request_website


class ClientPaymentRequestListView(APIView):
    """
    List payment requests belonging to the authenticated client within
    the current tenant.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanViewOwnPayments,
    ]
    

    def get(self, request: Request) -> Response:
        """
        List client payment requests.

        Args:
            request:
                Incoming DRF request.

        Returns:
            Response:
                Serialized client payment request summaries.
        """
        website = get_request_website(request)
        queryset = PaymentRequestSelector.get_queryset_for_client(
            website=website,
            client=request.user,
        ).order_by("-created_at")

        serializer = PaymentRequestSummarySerializer(
            queryset,
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClientPaymentRequestDetailView(APIView):
    """
    Retrieve a single payment request belonging to the authenticated
    client within the current tenant.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanViewOwnPayments,
    ]

    @staticmethod
    def _get_payment_request(
        *,
        website,
        client,
        payment_request_id: int,
    ) -> PaymentRequest:
        """
        Retrieve a client-scoped payment request.

        Args:
            website:
                Tenant website.
            client:
                Authenticated client.
            payment_request_id:
                Payment request primary key.

        Returns:
            PaymentRequest:
                Matching client-scoped payment request.
        """
        queryset = PaymentRequestSelector.get_queryset_for_client(
            website=website,
            client=client,
        )
        return get_object_or_404(
            queryset,
            pk=payment_request_id,
        )

    def get(
        self,
        request: Request,
        payment_request_id: int,
    ) -> Response:
        """
        Retrieve a client payment request summary by id.

        Args:
            request:
                Incoming DRF request.
            payment_request_id:
                Payment request primary key.

        Returns:
            Response:
                Serialized payment request summary.
        """
        website = get_request_website(request)
        payment_request = self._get_payment_request(
            website=website,
            client=request.user,
            payment_request_id=payment_request_id,
        )
        serializer = PaymentRequestSummarySerializer(payment_request)
        return Response(serializer.data, status=status.HTTP_200_OK)