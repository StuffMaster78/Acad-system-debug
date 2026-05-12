from __future__ import annotations

from typing import cast

from django.db.models import QuerySet
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from writer_compensation.api.serializers.reconciliation_serializers import (
    ReconciliationReportSerializer,
    RunReconciliationSerializer,
)
from writer_compensation.facade.payments_facade import CompensationFacade
from writer_compensation.models.payout_batch import PayoutBatch
from writer_compensation.models.payout_reconciliation_report import (
    PayoutReconciliationReport,
)
from writer_compensation.permissions.payout_permissions import (
    CanReconcilePayouts,
)


def _get_website(request):
    return request.website


def _error(message: str, code: int = 400) -> Response:
    return Response({"detail": message}, status=code)


class ReconciliationReportListView(generics.ListAPIView):
    """
    List reconciliation reports for the current website.
    """

    serializer_class = ReconciliationReportSerializer
    permission_classes = [CanReconcilePayouts]

    
    def get_queryset( # pyright: ignore[reportIncompatibleMethodOverride]
            self,
        ):
        queryset = (
            PayoutReconciliationReport.objects.filter(
                website=_get_website(self.request),
            )
            .select_related("payout_batch")
            .order_by("-created_at")
        )

        return cast(
            QuerySet[PayoutReconciliationReport],
            queryset,
        )


class RunReconciliationView(APIView):
    """
    Generate or refresh a reconciliation report for a payout batch.

    POST /reconciliation/run/

    Body:
    {
        "batch_id": int,
        "ledger_total": decimal,
        "payout_total": decimal,
        "cleared_total": decimal
    }
    """

    permission_classes = [CanReconcilePayouts]

    def post(self, request):
        website = _get_website(request)

        serializer = RunReconciliationSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        validated = cast(
            dict,
            serializer.validated_data,
        )

        try:
            batch = PayoutBatch.objects.get(
                pk=validated["batch_id"],
                website=website,
            )

        except PayoutBatch.DoesNotExist:
            return _error(
                "Batch not found.",
                status.HTTP_404_NOT_FOUND,
            )

        report = CompensationFacade.run_reconciliation(
            website=website,
            batch=batch,
            ledger_total=validated["ledger_total"],
            payout_total=validated["payout_total"],
            cleared_total=validated["cleared_total"],
        )

        response_serializer = ReconciliationReportSerializer(
            report,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )