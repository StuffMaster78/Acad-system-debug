
from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from writer_compensation.services.reconciliation_service import ReconciliationService
from writer_compensation.models.payout_batch import PayoutBatch
from writer_compensation.permissions.base import IsFinanceStaff
from wallets.models import Wallet

from typing import cast, Any
from typing import TypedDict
from decimal import Decimal


class ReconciliationRequestData(TypedDict):
    batch_id: int
    wallet_id: int
    ledger_total: Decimal
    payout_total: Decimal
    cleared_total: Decimal


class RunReconciliationView(APIView):

    permission_classes = [IsFinanceStaff]

    def post(self, request):
        data = cast(ReconciliationRequestData, request.data)

        batch = PayoutBatch.objects.get(pk=data["batch_id"])
        wallet = Wallet.objects.get(pk=data["wallet_id"])

        report = ReconciliationService.create_report(
            website=batch.website,
            batch=batch,
            ledger_total=data["ledger_total"],
            payout_total=data["payout_total"],
            cleared_total=data["cleared_total"],
        )

        return Response(
            {
                "id": report.pk,
                "status": report.status,
                "mismatch_amount": str(report.mismatch_amount),
                "batch_id": batch.pk,
                "wallet_balance": wallet.available_balance,
            },
            status=status.HTTP_200_OK,
        )