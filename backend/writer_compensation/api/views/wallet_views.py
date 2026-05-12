from __future__ import annotations

from rest_framework import generics

from writer_compensation.permissions.permissions import IsAdminUser
from writer_compensation.api.serializers.wallet_serializers import (
    WalletSerializer,
)

def _get_website(request):
    return request.website


class WalletListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]

    def get_serializer_class( # pyright: ignore[reportIncompatibleMethodOverride]
            self,
        ):
        return WalletSerializer

    def get_queryset( # pyright: ignore[reportIncompatibleMethodOverride]
            self,
        ): 
        from wallets.models import Wallet
        return Wallet.objects.filter(website=_get_website(self.request))


class WalletDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]

    def get_serializer_class( # pyright: ignore[reportIncompatibleMethodOverride]
            self,
        ):
        return WalletSerializer

    def get_queryset( # pyright: ignore[reportIncompatibleMethodOverride]
            self,
        ):
        from wallets.models.wallet import Wallet
        return Wallet.objects.filter(website=_get_website(self.request))