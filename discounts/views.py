from rest_framework import viewsets, permissions
from .models import Discount
from .serializers import DiscountSerializer

class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Filter by website if necessary
        return Discount.objects.filter(website=user.website) if hasattr(user, 'website') else Discount.objects.all()

    def perform_create(self, serializer):
        # Assign the discount to the user's website (if applicable)
        serializer.save(website=self.request.user.website)