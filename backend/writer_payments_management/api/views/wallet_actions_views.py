from __future__ import annotations

from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from wallets.services.wallet_service import WalletService
from wallets.selectors.wallet_selectors import WalletSelectors


class WalletCreditView(APIView):
    """
    Credit wallet safely.
    """

    def post(self, request):
        wallet = WalletSelectors.by_owner(
            website=request.user.website,
            owner_user=request.user,
        ).get(id=request.data["wallet_id"])

        amount = Decimal(request.data["amount"])

        entry = WalletService.credit_wallet(
            wallet=wallet,
            amount=amount,
            entry_type=request.data.get("entry_type", "manual"),
            website=request.user.website,
            created_by=request.user,
            description=request.data.get("description", ""),
        )

        return Response({"entry_id": entry.pk}, status=status.HTTP_201_CREATED)
    

class WalletDebitView(APIView):
    """
    Debit wallet safely.
    """

    def post(self, request):
        wallet = WalletSelectors.by_owner(
            website=request.user.website,
            owner_user=request.user,
        ).get(id=request.data["wallet_id"])

        amount = Decimal(request.data["amount"])

        entry = WalletService.debit_wallet(
            wallet=wallet,
            amount=amount,
            entry_type=request.data.get("entry_type", "manual"),
            website=request.user.website,
            created_by=request.user,
            description=request.data.get("description", ""),
            allow_negative=request.data.get("allow_negative", False),
        )

        return Response({"entry_id": entry.pk}, status=status.HTTP_201_CREATED)