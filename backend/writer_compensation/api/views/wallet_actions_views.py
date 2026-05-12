from __future__ import annotations

from decimal import Decimal

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from writer_compensation.permissions.permissions import IsAdminUser


def _get_website(request):
    return request.website


def _error(message: str, code: int = 400) -> Response:
    return Response({"detail": message}, status=code)


class WalletCreditView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        from writer_compensation.selectors.wallet_selectors import WalletSelectors
        from wallets.services.wallet_service import WalletService

        try:
            wallet = WalletSelectors.by_owner(
                website=_get_website(request),
                owner_user=request.user,
            ).get(id=request.data["wallet_id"])
        except Exception:
            return _error("Wallet not found.", 404)

        amount = Decimal(request.data["amount"])

        entry = WalletService.credit_wallet(
            wallet=wallet,
            amount=amount,
            entry_type=request.data.get("entry_type", "manual"),
            website=_get_website(request),
            created_by=request.user,
            description=request.data.get("description", ""),
        )

        return Response({"entry_id": entry.pk}, status=status.HTTP_201_CREATED)


class WalletDebitView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        from writer_compensation.selectors.wallet_selectors import WalletSelectors
        from wallets.services.wallet_service import WalletService

        try:
            wallet = WalletSelectors.by_owner(
                website=_get_website(request),
                owner_user=request.user,
            ).get(id=request.data["wallet_id"])
        except Exception:
            return _error("Wallet not found.", 404)

        amount = Decimal(request.data["amount"])

        entry = WalletService.debit_wallet(
            wallet=wallet,
            amount=amount,
            entry_type=request.data.get("entry_type", "manual"),
            website=_get_website(request),
            created_by=request.user,
            description=request.data.get("description", ""),
            allow_negative=request.data.get("allow_negative", False),
        )

        return Response({"entry_id": entry.pk}, status=status.HTTP_201_CREATED)