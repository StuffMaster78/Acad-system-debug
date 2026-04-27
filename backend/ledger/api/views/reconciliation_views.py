from __future__ import annotations

from typing import Any, cast

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from core.utils.request_context import get_request_website
from ledger.api.permissions.permissions import CanViewLedger
from ledger.api.serializers import ReconciliationSerializer
from ledger.models import ReconciliationRecord


class ReconciliationRecordListView(generics.ListAPIView):
    """
    List tenant-scoped reconciliation records.

    Reconciliation records are financial-control records, so the tenant
    filter is applied before any user-controlled query filters.
    """

    serializer_class = ReconciliationSerializer
    permission_classes = [
        IsAuthenticated,
        CanViewLedger,
    ]

    def get_queryset(self):
        """
        Return reconciliation records for request.website only.
        """
        request = cast(Request, self.request)
        website = get_request_website(request)

        queryset = ReconciliationRecord.objects.filter(
            website=website,
        ).order_by("-created_at")

        status_value = request.query_params.get("status")
        reference = request.query_params.get("reference")
        external_reference = request.query_params.get(
            "external_reference",
        )
        payment_intent_reference = request.query_params.get(
            "payment_intent_reference",
        )
        source_model = request.query_params.get("source_model")
        source_object_id = request.query_params.get("source_object_id")

        if status_value:
            queryset = queryset.filter(status=status_value)

        if reference:
            queryset = queryset.filter(reference=reference)

        if external_reference:
            queryset = queryset.filter(
                external_reference=external_reference,
            )

        if payment_intent_reference:
            queryset = queryset.filter(
                payment_intent_reference=payment_intent_reference,
            )

        if source_model:
            queryset = queryset.filter(source_model=source_model)

        if source_object_id:
            queryset = queryset.filter(source_object_id=source_object_id)

        return cast(Any, queryset)


class ReconciliationRecordDetailView(generics.RetrieveAPIView):
    """
    Retrieve one tenant-scoped reconciliation record.
    """

    serializer_class = ReconciliationSerializer
    permission_classes = [
        IsAuthenticated,
        CanViewLedger,
    ]
    lookup_field = "id"

    def get_queryset(self):
        """
        Return only reconciliation records for request.website.
        """
        request = cast(Request, self.request)
        website = get_request_website(request)

        queryset = ReconciliationRecord.objects.filter(
            website=website,
        )

        return cast(Any, queryset)