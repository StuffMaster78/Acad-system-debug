from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ClientProfile, LoyaltyTransaction
from .serializers import ClientProfileSerializer, LoyaltyTransactionSerializer


class ClientProfileDetailView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve a client's profile details.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ClientProfileSerializer

    def get_queryset(self):
        return ClientProfile.objects.filter(client=self.request.user)


class LoyaltyTransactionListView(generics.ListAPIView):
    """
    API endpoint to list loyalty transactions for a client.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LoyaltyTransactionSerializer

    def get_queryset(self):
        return LoyaltyTransaction.objects.filter(client__client=self.request.user)