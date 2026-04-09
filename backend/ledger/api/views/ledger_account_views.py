from typing import Any, cast

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from ledger.api.serializers import LedgerAccountSerializer
from ledger.models import LedgerAccount
from users.models import User


class LedgerAccountListView(generics.ListAPIView):
    serializer_class = LedgerAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        request = cast(Request, self.request)
        user = cast(User, request.user)

        queryset = LedgerAccount.objects.filter(
            website=user.website,
        ).order_by("account_type", "code")

        return cast(Any, queryset)


class LedgerAccountDetailView(generics.RetrieveAPIView):
    serializer_class = LedgerAccountSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        request = cast(Request, self.request)
        user = cast(User, request.user)

        queryset = LedgerAccount.objects.filter(
            website=user.website,
        )

        return cast(Any, queryset)