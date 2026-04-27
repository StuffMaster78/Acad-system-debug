from __future__ import annotations

from typing import Any, cast

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils.request_context import get_request_website
from wallets.api.permissions.permissions import (
    CanAdjustWallet,
    CanManageWalletHolds,
    CanReconcileWallet,
    CanViewWallets,
)
from wallets.api.serializers import (
    WalletEntrySerializer,
    WalletHoldSerializer,
    WalletSerializer,
)
from wallets.constants import WalletEntryType
from wallets.models import Wallet, WalletEntry, WalletHold
from wallets.services import (
    WalletHoldService,
    WalletReconciliationService,
    WalletService,
)


class AdminWalletQuerysetMixin:
    """
    Shared tenant-safe wallet lookup helpers.

    Important:
        Tenant resolution must come from request.website only.
        Never use request.user.website here.
    """

    def get_request(self) -> Request:
        return cast(Request, cast(Any, self).request)

    def get_website(self) -> Any:
        request = self.get_request()
        return get_request_website(request)

    def get_wallet(self, wallet_id: int) -> Wallet:
        website = self.get_website()

        return get_object_or_404(
            Wallet,
            id=wallet_id,
            website=website,
        )

    def get_hold(self, hold_id: int) -> WalletHold:
        website = self.get_website()

        return get_object_or_404(
            WalletHold,
            id=hold_id,
            website=website,
        )


class AdminWalletListView(AdminWalletQuerysetMixin, generics.ListAPIView):
    """
    List wallets for the resolved tenant.
    """

    serializer_class = WalletSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanViewWallets,
    ]

    def get_queryset(self) -> Any:
        website = self.get_website()

        return cast(
            Any,
            Wallet.objects.filter(website=website),
        )


class AdminWalletDetailView(AdminWalletQuerysetMixin, generics.RetrieveAPIView):
    """
    Retrieve one wallet for the resolved tenant.
    """

    serializer_class = WalletSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanViewWallets,
    ]

    def get_queryset(self) -> Any:
        website = self.get_website()

        return cast(
            Any,
            Wallet.objects.filter(website=website),
        )


class AdminWalletEntryListView(
    AdminWalletQuerysetMixin,
    generics.ListAPIView,
):
    """
    List entries for a tenant-scoped wallet.
    """

    serializer_class = WalletEntrySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanViewWallets,
    ]

    def get_queryset(self) -> Any:
        wallet = self.get_wallet(self.kwargs["wallet_id"])

        return cast(
            Any,
            WalletEntry.objects.filter(wallet=wallet).order_by("-created_at"),
        )


class AdminWalletHoldListView(
    AdminWalletQuerysetMixin,
    generics.ListAPIView,
):
    """
    List holds for a tenant-scoped wallet.
    """

    serializer_class = WalletHoldSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanViewWallets,
    ]

    def get_queryset(self) -> Any:
        wallet = self.get_wallet(self.kwargs["wallet_id"])

        return cast(
            Any,
            WalletHold.objects.filter(wallet=wallet).order_by("-created_at"),
        )


class AdminWalletFundView(AdminWalletQuerysetMixin, APIView):
    """
    Credit a tenant-scoped wallet through an internal admin action.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanAdjustWallet,
    ]

    def post(self, request: Request, wallet_id: int) -> Response:
        wallet = self.get_wallet(wallet_id)
        website = self.get_website()
        data = cast(dict[str, Any], request.data)

        entry = WalletService.credit_wallet(
            wallet=wallet,
            amount=data["amount"],
            entry_type=WalletEntryType.ADMIN_CREDIT,
            website=website,
            created_by=request.user,
            description=data.get("description", ""),
        )

        return Response(
            WalletEntrySerializer(entry).data,
            status=status.HTTP_201_CREATED,
        )


class AdminWalletDebitView(AdminWalletQuerysetMixin, APIView):
    """
    Debit a tenant-scoped wallet through an internal admin action.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanAdjustWallet,
    ]

    def post(self, request: Request, wallet_id: int) -> Response:
        wallet = self.get_wallet(wallet_id)
        website = self.get_website()
        data = cast(dict[str, Any], request.data)

        entry = WalletService.debit_wallet(
            wallet=wallet,
            amount=data["amount"],
            entry_type=WalletEntryType.ADMIN_DEBIT,
            website=website,
            created_by=request.user,
            description=data.get("description", ""),
        )

        return Response(
            WalletEntrySerializer(entry).data,
            status=status.HTTP_201_CREATED,
        )


class AdminWalletCreateHoldView(AdminWalletQuerysetMixin, APIView):
    """
    Create a hold against a tenant-scoped wallet.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanManageWalletHolds,
    ]

    def post(self, request: Request, wallet_id: int) -> Response:
        wallet = self.get_wallet(wallet_id)
        website = self.get_website()
        data = cast(dict[str, Any], request.data)

        hold = WalletHoldService.create_hold(
            wallet=wallet,
            amount=data["amount"],
            website=website,
            reason=data["reason"],
            created_by=request.user,
        )

        return Response(
            WalletHoldSerializer(hold).data,
            status=status.HTTP_201_CREATED,
        )


class AdminWalletReleaseHoldView(AdminWalletQuerysetMixin, APIView):
    """
    Release a tenant-scoped wallet hold.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanManageWalletHolds,
    ]

    def post(self, request: Request, hold_id: int) -> Response:
        hold = self.get_hold(hold_id)

        result = WalletHoldService.release_hold(
            hold=hold,
            released_by=request.user,
        )

        return Response(WalletHoldSerializer(result).data)


class AdminWalletCaptureHoldView(AdminWalletQuerysetMixin, APIView):
    """
    Capture a tenant-scoped wallet hold.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanManageWalletHolds,
    ]

    def post(self, request: Request, hold_id: int) -> Response:
        hold = self.get_hold(hold_id)

        result = WalletHoldService.capture_hold(
            hold=hold,
            captured_by=request.user,
        )

        return Response(WalletHoldSerializer(result).data)


class AdminWalletReconcileView(AdminWalletQuerysetMixin, APIView):
    """
    Reconcile a tenant-scoped wallet.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanReconcileWallet,
    ]

    def post(self, request: Request, wallet_id: int) -> Response:
        wallet = self.get_wallet(wallet_id)

        result = WalletReconciliationService.reconcile_wallet(
            wallet=wallet,
        )

        return Response(
            {
                "status": "ok",
                "wallet_id": result.wallet_id,
            },
            status=status.HTTP_200_OK,
        )


class AdminWalletRepairView(AdminWalletQuerysetMixin, APIView):
    """
    Repair cached wallet balances for a tenant-scoped wallet.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanReconcileWallet,
    ]

    def post(self, request: Request, wallet_id: int) -> Response:
        wallet = self.get_wallet(wallet_id)

        result = WalletReconciliationService.repair_wallet_balances(
            wallet=wallet,
            repaired_by=request.user,
        )

        return Response(
            {
                "status": "repaired",
                "wallet_id": result.wallet_id,
            },
            status=status.HTTP_200_OK,
        )