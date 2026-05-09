from __future__ import annotations

from rest_framework import generics

from writer_payments_management.api.serializers.exposure_serializers import (
    ExposureLedgerSerializer,
)
from writer_payments_management.models.exposure_ledger_models import (
    ExposureLedger,
)
from writer_payments_management.permissions.base import (
    IsFinanceStaff,
)


class ExposureLedgerListView(generics.ListAPIView):
    serializer_class = ExposureLedgerSerializer
    permission_classes = [IsFinanceStaff]

    queryset = (
        ExposureLedger.objects.select_related(
            "website",
            "writer",
        )
        .all()
        .order_by("-updated_at")
    )


class ExposureLedgerDetailView(generics.RetrieveAPIView):
    serializer_class = ExposureLedgerSerializer
    permission_classes = [IsFinanceStaff]

    queryset = (
        ExposureLedger.objects.select_related(
            "website",
            "writer",
        )
        .all()
    )