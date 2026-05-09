from __future__ import annotations

from rest_framework.views import APIView
from rest_framework.response import Response

from writer_payments_management.selectors.exposure_ledger_selectors import (
    ExposureLedgerSelectors,
)
from writer_payments_management.services.exposure_materialization_service import (
    ExposureMaterializationService,
)


class RebuildExposureView(APIView):
    """
    Force exposure recalculation.
    """

    def post(self, request):
        ledger = ExposureLedgerSelectors.by_writer(
            website=request.user.website,
            writer=request.user.writer_profile,
        ).get()

        ledger = ExposureMaterializationService.materialize(
            ledger=ledger,
        )

        return Response({
            "status": "rebuilt",
            "ledger_id": ledger.pk,
        })