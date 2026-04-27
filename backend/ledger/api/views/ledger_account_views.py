from __future__ import annotations

from typing import Any, cast

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from core.utils.request_context import get_request_website
from ledger.api.permissions.permissions import CanViewLedger
from ledger.api.serializers import LedgerAccountSerializer
from ledger.models import LedgerAccount


class LedgerAccountListView(generics.ListAPIView):
    """
    List tenant-scoped ledger accounts.

    Ledger accounts define how money is categorized for a website.
    Internal users may view only the tenant selected/resolved for the
    current request.
    """

    serializer_class = LedgerAccountSerializer
    permission_classes = [
        IsAuthenticated,
        CanViewLedger,
    ]

    def get_queryset(self):
        """
        Return ledger accounts for request.website only.
        """
        request = cast(Request, self.request)
        website = get_request_website(request)

        queryset = LedgerAccount.objects.filter(
            website=website,
        ).order_by("account_type", "code")

        return cast(Any, queryset)


class LedgerAccountDetailView(generics.RetrieveAPIView):
    """
    Retrieve one tenant-scoped ledger account.
    """

    serializer_class = LedgerAccountSerializer
    permission_classes = [
        IsAuthenticated,
        CanViewLedger,
    ]
    lookup_field = "id"

    def get_queryset(self):
        """
        Return only ledger accounts for request.website.
        """
        request = cast(Request, self.request)
        website = get_request_website(request)

        queryset = LedgerAccount.objects.filter(
            website=website,
        )

        return cast(Any, queryset)