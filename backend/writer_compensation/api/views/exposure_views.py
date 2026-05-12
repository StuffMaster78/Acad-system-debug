from __future__ import annotations

from rest_framework import generics

from writer_compensation.api.serializers.exposure_serializers import (
    ExposureLedgerSerializer,
)
from writer_compensation.models.exposure_ledger import (
    ExposureLedger,
)
from writer_compensation.permissions.base import (
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