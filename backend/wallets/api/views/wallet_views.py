from __future__ import annotations

from typing import Any, cast

from rest_framework.exceptions import ValidationError
from rest_framework import generics, permissions
from rest_framework.request import Request

from core.utils.request_context import get_request_website
from wallets.api.permissions.permissions import CanViewOwnWallet
from wallets.api.serializers import (
    WalletEntrySerializer,
    WalletHoldSerializer,
    WalletSerializer,
)
from wallets.models import WalletEntry, WalletHold
from wallets.services import WalletService


class MyWalletView(generics.RetrieveAPIView):
    """
    Retrieve the authenticated user's own wallet for the resolved tenant.
    """

    serializer_class = WalletSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanViewOwnWallet,
    ]

    def get_object(self) -> Any:
        request = cast(Request, self.request)
        website = get_request_website(request)
        user = cast(Any, request.user)

        wallet_type = request.query_params.get("wallet_type", "client")
        if wallet_type not in {"client", "writer"}:
            raise ValidationError("Invalid wallet type.")
        currency = request.query_params.get("currency", "USD")

        return WalletService.get_or_create_wallet(
            website=website,
            owner_user=user,
            wallet_type=wallet_type,
            currency=currency,
        )


class MyWalletEntryListView(generics.ListAPIView):
    """
    List entries for the authenticated user's own wallet.
    """

    serializer_class = WalletEntrySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanViewOwnWallet,
    ]

    def get_queryset(self) -> Any:
        request = cast(Request, self.request)
        website = get_request_website(request)
        user = cast(Any, request.user)

        wallet_type = request.query_params.get("wallet_type", "client")
        if wallet_type not in {"client", "writer"}:
            raise ValidationError("Invalid wallet type.")
        currency = request.query_params.get("currency", "USD")

        wallet = WalletService.get_or_create_wallet(
            website=website,
            owner_user=user,
            wallet_type=wallet_type,
            currency=currency,
        )

        queryset = WalletEntry.objects.filter(
            wallet=wallet,
            website=website,
        ).select_related(
            "wallet",
            "website",
            "created_by",
        ).order_by("-created_at", "-id")

        return cast(Any, queryset)


class MyWalletHoldListView(generics.ListAPIView):
    """
    List holds for the authenticated user's own wallet.
    """

    serializer_class = WalletHoldSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanViewOwnWallet,
    ]

    def get_queryset(self) -> Any:
        request = cast(Request, self.request)
        website = get_request_website(request)
        user = cast(Any, request.user)

        wallet_type = request.query_params.get("wallet_type", "client")
        if wallet_type not in {"client", "writer"}:
            raise ValidationError("Invalid wallet type.")
        currency = request.query_params.get("currency", "USD")

        wallet = WalletService.get_or_create_wallet(
            website=website,
            owner_user=user,
            wallet_type=wallet_type,
            currency=currency,
        )

        queryset = WalletHold.objects.filter(
            wallet=wallet,
            website=website,
        ).select_related(
            "wallet",
            "website",
            "created_by",
        ).order_by("-created_at", "-id")

        return cast(Any, queryset)