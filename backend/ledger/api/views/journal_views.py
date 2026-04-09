from typing import Any, cast

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from ledger.api.serializers import JournalEntrySerializer
from ledger.models import JournalEntry
from users.models import User


class JournalEntryListView(generics.ListAPIView):
    serializer_class = JournalEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        request = cast(Request, self.request)
        user = cast(User, request.user)

        queryset = JournalEntry.objects.filter(
            website=user.website,
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
    serializer_class = JournalEntrySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        request = cast(Request, self.request)
        user = cast(User, request.user)

        queryset = JournalEntry.objects.filter(
            website=user.website,
        )

        return cast(Any, queryset)