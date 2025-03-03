from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from django.utils.timezone import now
from django.db.models import Q
from .models import Discount, SeasonalEvent
from .serializers import DiscountSerializer, SeasonalEventSerializer

class SeasonalEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing seasonal events.
    Supports full CRUD operations.
    """
    queryset = SeasonalEvent.objects.all()
    serializer_class = SeasonalEventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """Ensure start_date is before end_date on creation."""
        event = serializer.save()
        if event.start_date >= event.end_date:
            raise ValidationError("End date must be after start date.")

class DiscountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing discounts.
    Supports full CRUD operations with optimized filtering.
    """
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Optimize queries:
        - Filter active discounts
        - Exclude expired ones
        """
        return Discount.objects.filter(
            Q(is_active=True) & 
            (Q(end_date__isnull=True) | Q(end_date__gte=now()))
        ).select_related("seasonal_event", "assigned_to_client")

    def perform_create(self, serializer):
        """Ensure discount data is valid before saving."""
        discount = serializer.save()
        
        # Validate discount type
        if discount.discount_type == "percentage" and not (1 <= discount.value <= 100):
            raise ValidationError("Percentage discount must be between 1 and 100.")

        # Ensure end_date is after start_date
        if discount.end_date and discount.start_date >= discount.end_date:
            raise ValidationError("End date must be after start date.")

        # Auto-disable expired discount
        if discount.end_date and discount.end_date < now():
            discount.is_active = False
            discount.save(update_fields=["is_active"])

    def perform_update(self, serializer):
        """Ensure discount remains valid on update."""
        discount = serializer.save()
        
        # Auto-disable expired discount
        if discount.end_date and discount.end_date < now():
            discount.is_active = False
            discount.save(update_fields=["is_active"])

    def destroy(self, request, *args, **kwargs):
        """
        Override delete to use soft deletion instead of hard deletion.
        """
        discount = self.get_object()
        discount.is_active = False  # Soft delete by deactivating
        discount.save(update_fields=["is_active"])
        return Response({"detail": "Discount deactivated."}, status=status.HTTP_204_NO_CONTENT)