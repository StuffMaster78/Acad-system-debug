from rest_framework import generics

from wallets.models import Wallet
from writer_payments_management.api.serializers.wallet_serializers import (
    WalletSerializer,
)


class WalletListView(generics.ListAPIView):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()


class WalletDetailView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()