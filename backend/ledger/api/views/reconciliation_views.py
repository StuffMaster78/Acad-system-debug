from typing import Any, cast

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from ledger.api.serializers import ReconciliationSerializer
from ledger.models import ReconciliationRecord
from users.models import User


class ReconciliationRecordListView(generics.ListAPIView):
    serializer_class = ReconciliationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        request = cast(Request, self.request)
        user = cast(User, request.user)

        queryset = ReconciliationRecord.objects.filter(
            website=user.website,
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
    serializer_class = ReconciliationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        request = cast(Request, self.request)
        user = cast(User, request.user)

        queryset = ReconciliationRecord.objects.filter(
            website=user.website,
        )

        return cast(Any, queryset)