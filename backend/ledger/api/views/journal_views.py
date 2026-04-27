from __future__ import annotations

from typing import Any, cast

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from core.utils.request_context import get_request_website
from ledger.api.permissions.permissions import CanViewLedger
from ledger.api.serializers import JournalEntrySerializer
from ledger.models import JournalEntry


class JournalEntryListView(generics.ListAPIView):
    """
    List tenant-scoped journal entries.

    Tenant source:
        request.website, resolved by middleware.

    Security:
        Only internal users with ledger.view may access this endpoint.
    """

    serializer_class = JournalEntrySerializer
    permission_classes = [
        IsAuthenticated,
        CanViewLedger,
    ]

    def get_queryset(self):
        """
        Return journal entries for the resolved tenant.

        Query filters are allowed only after tenant scoping has already
        been applied. This prevents cross-tenant financial data exposure.
        """
        request = cast(Request, self.request)
        website = get_request_website(request)

        queryset = JournalEntry.objects.filter(
            website=website,
        ).order_by("-created_at")

        entry_type = request.query_params.get("entry_type")
        status_value = request.query_params.get("status")
        reference = request.query_params.get("reference")
        source_model = request.query_params.get("source_model")
        source_object_id = request.query_params.get("source_object_id")
        payment_intent_reference = request.query_params.get(
            "payment_intent_reference",
        )
        external_reference = request.query_params.get(
            "external_reference",
        )

        if entry_type:
            queryset = queryset.filter(entry_type=entry_type)

        if status_value:
            queryset = queryset.filter(status=status_value)

        if reference:
            queryset = queryset.filter(reference=reference)

        if source_model:
            queryset = queryset.filter(source_model=source_model)

        if source_object_id:
            queryset = queryset.filter(source_object_id=source_object_id)

        if payment_intent_reference:
            queryset = queryset.filter(
                payment_intent_reference=payment_intent_reference,
            )

        if external_reference:
            queryset = queryset.filter(
                external_reference=external_reference,
            )

        return cast(Any, queryset)


class JournalEntryDetailView(generics.RetrieveAPIView):
    """
    Retrieve one tenant-scoped journal entry.
    """

    serializer_class = JournalEntrySerializer
    permission_classes = [
        IsAuthenticated,
        CanViewLedger,
    ]
    lookup_field = "id"

    def get_queryset(self):
        """
        Return only journal entries for the resolved tenant.
        """
        request = cast(Request, self.request)
        website = get_request_website(request)

        queryset = JournalEntry.objects.filter(
            website=website,
        )

        return cast(Any, queryset)