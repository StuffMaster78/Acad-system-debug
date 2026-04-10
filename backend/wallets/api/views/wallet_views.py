from __future__ import annotations

from typing import Any, cast

from rest_framework import generics, permissions
from rest_framework.request import Request

from wallets.api.serializers import (
    WalletEntrySerializer,
    WalletHoldSerializer,
    WalletSerializer,
)
from wallets.models import WalletEntry, WalletHold
from wallets.services import WalletService


class MyWalletView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> Any:
        request = cast(Request, self.request)
        user = cast(Any, request.user)

        wallet_type = request.query_params.get("wallet_type", "client")
        currency = request.query_params.get("currency", "USD")

        return WalletService.get_or_create_wallet(
            website=user.website,
            owner_user=user,
            wallet_type=wallet_type,
            currency=currency,
        )


class MyWalletEntryListView(generics.ListAPIView):
    serializer_class = WalletEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        request = cast(Request, self.request)
        user = cast(Any, request.user)

        wallet_type = request.query_params.get("wallet_type", "client")
        currency = request.query_params.get("currency", "USD")

        wallet = WalletService.get_or_create_wallet(
            website=user.website,
            owner_user=user,
            wallet_type=wallet_type,
            currency=currency,
        )

        queryset = WalletEntry.objects.filter(wallet=wallet).select_related(
            "wallet",
            "website",
            "created_by",
        ).order_by("-created_at", "-id")

        return cast(Any, queryset)


class MyWalletHoldListView(generics.ListAPIView):
    serializer_class = WalletHoldSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        request = cast(Request, self.request)
        user = cast(Any, request.user)

        wallet_type = request.query_params.get("wallet_type", "client")
        currency = request.query_params.get("currency", "USD")

        wallet = WalletService.get_or_create_wallet(
            website=user.website,
            owner_user=user,
            wallet_type=wallet_type,
            currency=currency,
        )

        queryset = WalletHold.objects.filter(wallet=wallet).select_related(
            "wallet",
            "website",
            "created_by",
        ).order_by("-created_at", "-id")

        return cast(Any, queryset)