from __future__ import annotations

from typing import Any, cast

from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from wallets.api.permissions import IsWalletAdminOrSuperAdmin
from wallets.api.serializers import (
    AdminCreateWalletHoldSerializer,
    AdminWalletDebitSerializer,
    AdminWalletFundSerializer,
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


# ----------------------------
# Shared mixin
# ----------------------------
class AdminWalletQuerysetMixin:
    def get_request_user(self) -> Any:
        request = cast(Request, cast(Any, self).request)
        return cast(Any, request.user)

    def get_wallet(self, wallet_id: int) -> Wallet:
        user = self.get_request_user()
        return Wallet.objects.get(id=wallet_id, website=user.website)

    def get_hold(self, hold_id: int) -> WalletHold:
        user = self.get_request_user()
        return WalletHold.objects.get(id=hold_id, website=user.website)


# ----------------------------
# READ VIEWS
# ----------------------------
class AdminWalletListView(AdminWalletQuerysetMixin, generics.ListAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated, IsWalletAdminOrSuperAdmin]

    def get_queryset(self) -> Any:
        user = self.get_request_user()
        return cast(Any, Wallet.objects.filter(website=user.website))


class AdminWalletDetailView(AdminWalletQuerysetMixin, generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated, IsWalletAdminOrSuperAdmin]

    def get_queryset(self) -> Any:
        user = self.get_request_user()
        return cast(Any, Wallet.objects.filter(website=user.website))


class AdminWalletEntryListView(AdminWalletQuerysetMixin, generics.ListAPIView):
    serializer_class = WalletEntrySerializer
    permission_classes = [permissions.IsAuthenticated, IsWalletAdminOrSuperAdmin]

    def get_queryset(self) -> Any:
        wallet = self.get_wallet(self.kwargs["wallet_id"])
        return cast(Any, WalletEntry.objects.filter(wallet=wallet))


class AdminWalletHoldListView(AdminWalletQuerysetMixin, generics.ListAPIView):
    serializer_class = WalletHoldSerializer
    permission_classes = [permissions.IsAuthenticated, IsWalletAdminOrSuperAdmin]

    def get_queryset(self) -> Any:
        wallet = self.get_wallet(self.kwargs["wallet_id"])
        return cast(Any, WalletHold.objects.filter(wallet=wallet))


# ----------------------------
# MUTATION VIEWS
# ----------------------------
class AdminWalletFundView(AdminWalletQuerysetMixin, APIView):
    permission_classes = [permissions.IsAuthenticated, IsWalletAdminOrSuperAdmin]

    def post(self, request: Request, wallet_id: int):
        wallet = self.get_wallet(wallet_id)
        data = cast(dict[str, Any], request.data)
        user = cast(Any, request.user)

        entry = WalletService.credit_wallet(
            wallet=wallet,
            amount=data["amount"],
            entry_type=WalletEntryType.ADMIN_CREDIT,
            website=user.website,
            created_by=user,
            description=data.get("description", ""),
        )

        return Response(WalletEntrySerializer(entry).data, status=201)


class AdminWalletDebitView(AdminWalletQuerysetMixin, APIView):
    permission_classes = [permissions.IsAuthenticated, IsWalletAdminOrSuperAdmin]

    def post(self, request: Request, wallet_id: int):
        wallet = self.get_wallet(wallet_id)
        data = cast(dict[str, Any], request.data)
        user = cast(Any, request.user)

        entry = WalletService.debit_wallet(
            wallet=wallet,
            amount=data["amount"],
            entry_type=WalletEntryType.ADMIN_DEBIT,
            website=user.website,
            created_by=user,
            description=data.get("description", ""),
        )

        return Response(WalletEntrySerializer(entry).data, status=201)


class AdminWalletCreateHoldView(AdminWalletQuerysetMixin, APIView):
    permission_classes = [permissions.IsAuthenticated, IsWalletAdminOrSuperAdmin]

    def post(self, request: Request, wallet_id: int):
        wallet = self.get_wallet(wallet_id)
        data = cast(dict[str, Any], request.data)
        user = cast(Any, request.user)

        hold = WalletHoldService.create_hold(
            wallet=wallet,
            amount=data["amount"],
            website=user.website,
            reason=data["reason"],
            created_by=user,
        )

        return Response(WalletHoldSerializer(hold).data, status=201)


class AdminWalletReleaseHoldView(AdminWalletQuerysetMixin, APIView):
    permission_classes = [permissions.IsAuthenticated, IsWalletAdminOrSuperAdmin]

    def post(self, request: Request, hold_id: int):
        hold = self.get_hold(hold_id)
        user = cast(Any, request.user)

        result = WalletHoldService.release_hold(hold=hold, released_by=user)
        return Response(WalletHoldSerializer(result).data)


class AdminWalletCaptureHoldView(AdminWalletQuerysetMixin, APIView):
    permission_classes = [permissions.IsAuthenticated, IsWalletAdminOrSuperAdmin]

    def post(self, request: Request, hold_id: int):
        hold = self.get_hold(hold_id)
        user = cast(Any, request.user)

        result = WalletHoldService.capture_hold(hold=hold, captured_by=user)
        return Response(WalletHoldSerializer(result).data)


class AdminWalletReconcileView(AdminWalletQuerysetMixin, APIView):
    permission_classes = [permissions.IsAuthenticated, IsWalletAdminOrSuperAdmin]

    def post(self, request: Request, wallet_id: int):
        wallet = self.get_wallet(wallet_id)
        result = WalletReconciliationService.reconcile_wallet(wallet=wallet)
        return Response({"status": "ok", "wallet_id": result.wallet_id})


class AdminWalletRepairView(AdminWalletQuerysetMixin, APIView):
    permission_classes = [permissions.IsAuthenticated, IsWalletAdminOrSuperAdmin]

    def post(self, request: Request, wallet_id: int):
        wallet = self.get_wallet(wallet_id)
        user = cast(Any, request.user)

        result = WalletReconciliationService.repair_wallet_balances(
            wallet=wallet,
            repaired_by=user,
        )

        return Response({"status": "repaired", "wallet_id": result.wallet_id})