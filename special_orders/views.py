from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import (
    SpecialOrder, 
    InstallmentPayment, 
    PredefinedSpecialOrderConfig, 
    PredefinedSpecialOrderDuration, 
    WriterBonus
)
from .serializers import (
    SpecialOrderSerializer, 
    InstallmentPaymentSerializer, 
    PredefinedSpecialOrderConfigSerializer, 
    PredefinedSpecialOrderDurationSerializer, 
    WriterBonusSerializer
)

# 🔹 Special Order API ViewSet
class SpecialOrderViewSet(viewsets.ModelViewSet):
    """
    API for managing Special Orders.
    """
    queryset = SpecialOrder.objects.all().select_related('client', 'writer', 'predefined_type')
    serializer_class = SpecialOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter orders based on user role."""
        user = self.request.user
        if user.is_staff:
            return SpecialOrder.objects.all()
        return SpecialOrder.objects.filter(client=user)

    def perform_create(self, serializer):
        """Automatically set the client when creating an order."""
        serializer.save(client=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        """Admin can approve an order."""
        special_order = self.get_object()
        special_order.is_approved = True
        special_order.save()
        return Response({'status': 'Order approved'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def override_payment(self, request, pk=None):
        """Admin can manually mark an order as paid."""
        special_order = self.get_object()
        special_order.admin_marked_paid = True
        special_order.save()
        return Response({'status': 'Payment overridden'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete_order(self, request, pk=None):
        """Mark an order as completed (client or admin can confirm)."""
        special_order = self.get_object()
        special_order.status = 'completed'
        special_order.save()
        return Response({'status': 'Order marked as completed'}, status=status.HTTP_200_OK)


# 🔹 Installment Payment API ViewSet
class InstallmentPaymentViewSet(viewsets.ModelViewSet):
    """
    API for managing Installment Payments.
    """
    queryset = InstallmentPayment.objects.all().select_related('special_order')
    serializer_class = InstallmentPaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter installments based on user role."""
        user = self.request.user
        if user.is_staff:
            return InstallmentPayment.objects.all()
        return InstallmentPayment.objects.filter(special_order__client=user)

    def perform_create(self, serializer):
        """Ensure installment is linked to an order owned by the client."""
        special_order = serializer.validated_data['special_order']
        if special_order.client != self.request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()


# 🔹 Predefined Special Orders API ViewSet
class PredefinedSpecialOrderConfigViewSet(viewsets.ModelViewSet):
    """
    API for predefined special order configurations.
    """
    queryset = PredefinedSpecialOrderConfig.objects.all()
    serializer_class = PredefinedSpecialOrderConfigSerializer
    permission_classes = [IsAdminUser]


# 🔹 Predefined Special Order Durations API ViewSet
class PredefinedSpecialOrderDurationViewSet(viewsets.ModelViewSet):
    """
    API for predefined special order durations.
    """
    queryset = PredefinedSpecialOrderDuration.objects.all()
    serializer_class = PredefinedSpecialOrderDurationSerializer
    permission_classes = [IsAdminUser]


# 🔹 Writer Bonus API ViewSet
class WriterBonusViewSet(viewsets.ModelViewSet):
    """
    API for managing writer bonuses.
    """
    queryset = WriterBonus.objects.all().select_related('writer', 'special_order')
    serializer_class = WriterBonusSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """Admins can view all bonuses, writers can only see their own."""
        user = self.request.user
        if user.is_staff:
            return WriterBonus.objects.all()
        return WriterBonus.objects.filter(writer=user)

    def perform_create(self, serializer):
        """Admin sets writer bonuses."""
        serializer.save()