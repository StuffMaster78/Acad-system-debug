from rest_framework import generics

from wallets.models import Wallet
from writer_compensation.api.serializers.wallet_serializers import (
    WalletSerializer,
)


class WalletListView(generics.ListAPIView):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()


class WalletDetailView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()