from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import (
    SpecialOrder,
    InstallmentPayment,
    PredefinedSpecialOrderConfig,
    PredefinedSpecialOrderDuration,
    WriterBonus,
    EstimatedSpecialOrderSettings
)
from .serializers import (
    SpecialOrderSerializer,
    InstallmentPaymentSerializer,
    PredefinedSpecialOrderConfigSerializer,
    PredefinedSpecialOrderDurationSerializer,
    WriterBonusSerializer,
    EstimatedSpecialOrderSettingsSerializer
)
from .services.special_order_service import SpecialOrderService
from .services.installment_payment_service import InstallmentPaymentService
import logging

logger = logging.getLogger("special_orders")


class SpecialOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing special orders.
    """
    queryset = SpecialOrder.objects.select_related(
        'client', 'writer', 'predefined_type'
    )
    serializer_class = SpecialOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return filtered queryset based on user role.
        """
        user = self.request.user
        if user.is_staff:
            return SpecialOrder.objects.all()
        return SpecialOrder.objects.filter(client=user)

    def perform_create(self, serializer):
        """
        Assign the current user as client on creation.
        """
        serializer.save(client=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        """
        Admin endpoint to approve a special order.
        """
        order = self.get_object()
        SpecialOrderService.approve_special_order(order)
        logger.info(f"Order #{order.id} approved by admin.")
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def override_payment(self, request, pk=None):
        """
        Admin endpoint to override payment status.
        """
        order = self.get_object()
        SpecialOrderService.override_payment(order)
        logger.info(f"Payment overridden for order #{order.id}")
        return Response({'status': 'payment overridden'})

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def complete_order(self, request, pk=None):
        """
        Mark a special order as completed.
        """
        order = self.get_object()
        SpecialOrderService.complete_special_order(order)
        logger.info(f"Order #{order.id} marked as completed.")
        return Response({'status': 'order completed'})


class InstallmentPaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing installment payments.
    """
    queryset = InstallmentPayment.objects.select_related('special_order')
    serializer_class = InstallmentPaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter installments based on user role.
        """
        user = self.request.user
        if user.is_staff:
            return InstallmentPayment.objects.all()
        return InstallmentPayment.objects.filter(
            special_order__client=user
        )

    def perform_create(self, serializer):
        """
        Validate client ownership and save installment.
        """
        user = self.request.user
        try:
            InstallmentPaymentService.validate_and_save_installment(serializer, user)
        except PermissionError as e:
            logger.warning(str(e))
            raise PermissionError(str(e))


class PredefinedSpecialOrderConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for predefined special order configs.
    """
    queryset = PredefinedSpecialOrderConfig.objects.all()
    serializer_class = PredefinedSpecialOrderConfigSerializer
    permission_classes = [IsAdminUser]


class PredefinedSpecialOrderDurationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for predefined special order durations.
    """
    queryset = PredefinedSpecialOrderDuration.objects.all()
    serializer_class = PredefinedSpecialOrderDurationSerializer
    permission_classes = [IsAdminUser]


class WriterBonusViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing writer bonuses.
    """
    queryset = WriterBonus.objects.select_related(
        'writer', 'special_order'
    )
    serializer_class = WriterBonusSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """
        Filter bonuses by writer or return all for admin.
        """
        user = self.request.user
        if user.is_staff:
            return WriterBonus.objects.all()
        return WriterBonus.objects.filter(writer=user)

    def perform_create(self, serializer):
        """
        Save writer bonus.
        """
        serializer.save()

class EstimatedSpecialOrderSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Estimated Special Order deposit settings.
    """
    queryset = EstimatedSpecialOrderSettings.objects.all()
    serializer_class = EstimatedSpecialOrderSettingsSerializer
    permission_classes = [IsAdminUser]