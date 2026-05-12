from __future__ import annotations

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from writer_compensation.api.serializers.exposure_serializers import (
    ExposureLedgerSerializer,
)
from writer_compensation.exceptions.exceptions import CompensationError
from writer_compensation.facade.payments_facade import CompensationFacade
from writer_compensation.models.exposure_ledger import ExposureLedger
from writer_compensation.permissions.payout_permissions import CanViewPayouts
from writer_compensation.permissions.permissions import IsAdminUser


def _get_website(request):
    return request.website


def _error(message: str, code: int = 400) -> Response:
    return Response({"detail": message}, status=code)


class ExposureLedgerListView(generics.ListAPIView):
    serializer_class   = ExposureLedgerSerializer
    permission_classes = [CanViewPayouts]

    def get_queryset(  # pyright: ignore[reportIncompatibleMethodOverride]
            self
        ):
        return (
            ExposureLedger.objects
            .filter(website=_get_website(self.request))
            .select_related("writer")
            .order_by("-last_updated")
        )


class ExposureLedgerDetailView(generics.RetrieveAPIView):
    serializer_class   = ExposureLedgerSerializer
    permission_classes = [CanViewPayouts]

    def get_queryset(  # pyright: ignore[reportIncompatibleMethodOverride]
            self
        ):
        return ExposureLedger.objects.filter(
            website=_get_website(self.request),
        )


class ExposureRecomputeView(APIView):
    """
    POST /exposure/{pk}/recompute/
    Full authoritative recompute of an exposure ledger from the raw event log.
    Use for drift detection, reconciliation, and disaster recovery.
    """
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        website = _get_website(request)
        try:
            ledger = ExposureLedger.objects.get(pk=pk, website=website)
        except ExposureLedger.DoesNotExist:
            return _error("Exposure ledger not found.", 404)

        try:
            ledger = CompensationFacade.recompute_exposure(
                website=website,
                writer=ledger.writer,
            )
        except CompensationError as exc:
            return _error(str(exc), 409)

        return Response(ExposureLedgerSerializer(ledger).data)