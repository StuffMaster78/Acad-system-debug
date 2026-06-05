from __future__ import annotations

from typing import Any, cast

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils.request_context import get_request_website
from notifications_system.services.notification_service import NotificationService
from wallets.api.permissions.permissions import (
    CanAdjustWallet,
    CanManageWalletHolds,
    CanReconcileWallet,
    CanViewWallets,
)
from wallets.api.serializers import (
    AdminEnsureWalletSerializer,
    AdminCreateWalletHoldSerializer,
    AdminWalletDebitSerializer,
    AdminWalletFundSerializer,
    WalletEntrySerializer,
    WalletHoldSerializer,
    WalletSerializer,
)
from wallets.constants import WalletEntryType
from wallets.models import Wallet, WalletEntry, WalletHold
from wallets.selectors import WalletEntrySelectors, WalletHoldSelectors, WalletSelectors
from wallets.services import (
    WalletHoldService,
    WalletReconciliationService,
    WalletService,
)
from wallets.services.wallet_ledger_integration_service import (
    WalletLedgerIntegrationService,
)
from websites.models.websites import Website


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
        user = request.user
        if (
            getattr(user, "is_superuser", False)
            or getattr(user, "role", None) == "superadmin"
        ):
            website_id = request.query_params.get("website_id") or request.data.get(
                "website_id"
            )
            if website_id:
                return get_object_or_404(
                    Website,
                    id=website_id,
                    is_active=True,
                    is_deleted=False,
                )
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
            WalletSelectors.for_website(website=website),
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
            WalletSelectors.for_website(website=website),
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
            WalletEntrySelectors.for_wallet(wallet=wallet).order_by(
                "-created_at",
                "-id",
            ),
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
            WalletHoldSelectors.for_wallet(wallet=wallet).order_by(
                "-created_at",
                "-id",
            ),
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
        serializer = AdminWalletFundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        journal_entry = WalletLedgerIntegrationService.post_admin_credit(
            website=website,
            wallet=wallet,
            amount=data["amount"],
            created_by=request.user,
            reference=data.get("reference", ""),
            source_object_id=data.get("reference_id", ""),
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
        )

        entry = WalletService.credit_wallet(
            wallet=wallet,
            amount=data["amount"],
            entry_type=WalletEntryType.ADMIN_CREDIT,
            website=website,
            created_by=request.user,
            description=data.get("description", ""),
            reference=data.get("reference", ""),
            reference_type=data.get("reference_type", "admin_funding"),
            reference_id=data.get("reference_id", ""),
            metadata=data.get("metadata", {}),
        )
        entry.ledger_transaction = journal_entry
        entry.save(update_fields=["ledger_transaction", "updated_at"])
        self._notify_wallet_owner(
            event_key="wallet.credited",
            wallet=wallet,
            amount=data["amount"],
            entry=entry,
            triggered_by=request.user,
        )

        return Response(
            WalletEntrySerializer(entry).data,
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _notify_wallet_owner(
        *,
        event_key: str,
        wallet: Wallet,
        amount: Any,
        entry: WalletEntry,
        triggered_by: Any,
    ) -> None:
        owner = getattr(wallet, "owner_user", None)
        if owner is None:
            return
        NotificationService.notify(
            event_key=event_key,
            recipient=owner,
            website=wallet.website,
            context={
                "amount": str(amount),
                "currency": wallet.currency,
                "wallet_id": wallet.pk,
                "wallet_entry_id": entry.pk,
                "new_balance": str(wallet.available_balance),
            },
            triggered_by=triggered_by,
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
        serializer = AdminWalletDebitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        journal_entry = WalletLedgerIntegrationService.post_admin_debit(
            website=website,
            wallet=wallet,
            amount=data["amount"],
            created_by=request.user,
            reference=data.get("reference", ""),
            source_object_id=data.get("reference_id", ""),
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
        )

        entry = WalletService.debit_wallet(
            wallet=wallet,
            amount=data["amount"],
            entry_type=WalletEntryType.ADMIN_DEBIT,
            website=website,
            created_by=request.user,
            description=data.get("description", ""),
            reference=data.get("reference", ""),
            reference_type=data.get("reference_type", "admin_debit"),
            reference_id=data.get("reference_id", ""),
            metadata=data.get("metadata", {}),
        )
        entry.ledger_transaction = journal_entry
        entry.save(update_fields=["ledger_transaction", "updated_at"])
        AdminWalletFundView._notify_wallet_owner(
            event_key="wallet.debited",
            wallet=wallet,
            amount=data["amount"],
            entry=entry,
            triggered_by=request.user,
        )

        return Response(
            WalletEntrySerializer(entry).data,
            status=status.HTTP_201_CREATED,
        )


class AdminEnsureWalletView(AdminWalletQuerysetMixin, APIView):
    """
    Ensure a client or writer wallet exists for the resolved tenant.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanAdjustWallet,
    ]

    def post(self, request: Request) -> Response:
        website = self.get_website()
        serializer = AdminEnsureWalletSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        User = get_user_model()
        user_queryset = User.objects.filter(
            website=website,
            role=data["wallet_type"],
            is_active=True,
        )
        if data.get("user_id"):
            user_queryset = user_queryset.filter(id=data["user_id"])
        else:
            lookup = data["user_lookup"]
            user_queryset = user_queryset.filter(
                Q(email__iexact=lookup)
                | Q(username__iexact=lookup)
                | Q(first_name__icontains=lookup)
                | Q(last_name__icontains=lookup)
            )
        user = get_object_or_404(user_queryset.order_by("id"))
        wallet = WalletService.get_or_create_wallet(
            website=website,
            owner_user=user,
            wallet_type=data["wallet_type"],
            currency=data.get("currency", "USD"),
        )

        return Response(WalletSerializer(wallet).data, status=status.HTTP_200_OK)


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
        serializer = AdminCreateWalletHoldSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        hold = WalletHoldService.create_hold(
            wallet=wallet,
            amount=data["amount"],
            website=website,
            reason=data["reason"],
            created_by=request.user,
            reference=data.get("reference", ""),
            reference_type=data.get("reference_type", ""),
            reference_id=data.get("reference_id", ""),
            expires_at=data.get("expires_at"),
            metadata=data.get("metadata", {}),
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
