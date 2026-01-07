from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.core.exceptions import ValidationError

from special_orders.models import (
    SpecialOrder,
    InstallmentPayment,
    PredefinedSpecialOrderConfig,
    PredefinedSpecialOrderDuration,
    WriterBonus,
    EstimatedSpecialOrderSettings
)
from special_orders.serializers import (
    SpecialOrderSerializer,
    InstallmentPaymentSerializer,
    PredefinedSpecialOrderConfigSerializer,
    PredefinedSpecialOrderDurationSerializer,
    WriterBonusSerializer,
    EstimatedSpecialOrderSettingsSerializer
)
from special_orders.services.special_order_service import SpecialOrderService
from special_orders.services.installment_payment_service import InstallmentPaymentService
from special_orders.services.order_approval import OrderApprovalService
from special_orders.services.installment_payment_processor import SpecialOrderInstallmentPaymentService
from special_orders.services.streamlined_order_service import StreamlinedSpecialOrderService
import logging

logger = logging.getLogger("special_orders")


class SpecialOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing special orders.
    """
    queryset = SpecialOrder.objects.select_related(
        'client', 'writer', 'predefined_type'
    ).order_by('-created_at')
    serializer_class = SpecialOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return filtered queryset based on user role.
        """
        user = self.request.user
        if user.is_staff:
            return SpecialOrder.objects.all().order_by('-created_at')
        return SpecialOrder.objects.filter(client=user).order_by('-created_at')

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
        OrderApprovalService.approve_special_order(order, request.user)
        logger.info(f"Order #{order.id} approved by admin {request.user.username}.")
        return Response({
            'status': 'approved',
            'order_status': order.status,
            'message': f"Order approved. Status: {order.status}"
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def override_payment(self, request, pk=None):
        """
        Admin endpoint to override payment status.
        """
        order = self.get_object()
        SpecialOrderService.override_payment(order)
        logger.info(f"Payment overridden for order #{order.id}")
        return Response({'status': 'payment overridden'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def assign_writer(self, request, pk=None):
        """
        Admin assigns a writer to a special order with optional payment amount or percentage.
        
        Request body:
        {
            "writer_id": 123,
            "payment_amount": 100.00,  // Optional: fixed payment amount
            "payment_percentage": 15.5,  // Optional: percentage of order total
            "admin_notes": "Optional notes"
        }
        Note: Provide either payment_amount OR payment_percentage, not both.
        """
        from django.contrib.auth import get_user_model
        from decimal import Decimal
        from special_orders.services.writer_assignment import assign_writer as assign_special_order_writer
        
        User = get_user_model()
        order = self.get_object()
        
        writer_id = request.data.get('writer_id')
        payment_amount = request.data.get('payment_amount')
        payment_percentage = request.data.get('payment_percentage')
        admin_notes = request.data.get('admin_notes', '')
        
        if not writer_id:
            return Response(
                {'error': 'writer_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            writer = User.objects.get(id=writer_id, role='writer', is_active=True)
        except User.DoesNotExist:
            return Response(
                {'error': 'Writer not found or not active.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Convert payment values to Decimal if provided
        payment_amount_decimal = None
        payment_percentage_decimal = None
        
        if payment_amount is not None:
            try:
                payment_amount_decimal = Decimal(str(payment_amount))
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid payment_amount format.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if payment_percentage is not None:
            try:
                payment_percentage_decimal = Decimal(str(payment_percentage))
                if payment_percentage_decimal < 0 or payment_percentage_decimal > 100:
                    return Response(
                        {'error': 'payment_percentage must be between 0 and 100.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid payment_percentage format.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            # Assign writer with payment info
            assign_special_order_writer(
                order, 
                writer, 
                payment_amount=payment_amount_decimal,
                payment_percentage=payment_percentage_decimal
            )
            
            # Update admin notes if provided
            if admin_notes:
                order.admin_notes = (order.admin_notes or '') + '\n' + admin_notes
                order.save()
            
            # Update status if needed
            if order.status == 'awaiting_approval':
                order.status = 'in_progress'
                order.save()
            
            logger.info(f"Writer {writer.username} assigned to special order #{order.id} with payment: amount={payment_amount_decimal}, percentage={payment_percentage_decimal}")
            
            return Response(
                SpecialOrderSerializer(order).data,
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception(f"Error assigning writer to special order: {e}")
            return Response(
                {'error': 'An error occurred assigning the writer.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def complete_order(self, request, pk=None):
        """
        Mark a special order as completed.
        Uses streamlined service for better workflow management.
        """
        order = self.get_object()
        try:
            completed_order = StreamlinedSpecialOrderService.complete_order(
                order=order,
                completed_by=request.user,
                files_uploaded=request.data.get('files_uploaded', True),
                completion_notes=request.data.get('completion_notes')
            )
            serializer = SpecialOrderSerializer(completed_order)
            logger.info(f"Order #{order.id} marked as completed by {request.user.username}.")
            return Response({
                'status': 'order completed',
                'order': serializer.data
            })
        except Exception as e:
            logger.exception(f"Error completing order: {e}")
            # Fallback to old method for backward compatibility
            SpecialOrderService.complete_special_order(order)
            return Response({'status': 'order completed'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser], url_path='set-price')
    def set_price(self, request, pk=None):
        """
        Set or negotiate price for an estimated order (streamlined).
        Can be called multiple times for negotiation.
        """
        order = self.get_object()
        try:
            updated_order = StreamlinedSpecialOrderService.set_price(
                order=order,
                admin_user=request.user,
                total_cost=request.data.get('total_cost'),
                price_per_day=request.data.get('price_per_day'),
                admin_notes=request.data.get('admin_notes')
            )
            serializer = SpecialOrderSerializer(updated_order)
            return Response(serializer.data)
        except Exception as e:
            logger.exception(f"Error setting price: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'], url_path='workflow-status')
    def workflow_status(self, request, pk=None):
        """
        Get current workflow status and available actions.
        """
        order = self.get_object()
        status_info = StreamlinedSpecialOrderService.get_order_workflow_status(
            order=order,
            user=request.user
        )
        return Response(status_info)


class InstallmentPaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing installment payments.
    """
    queryset = InstallmentPayment.objects.select_related('special_order', 'payment_record')
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
        Note: Use pay_installment action to actually process payment.
        """
        user = self.request.user
        try:
            InstallmentPaymentService.validate_and_save_installment(serializer, user)
        except PermissionError as e:
            logger.warning(str(e))
            raise PermissionError(str(e))
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def pay_installment(self, request, pk=None):
        """
        Process payment for a specific installment.
        
        Request body:
        {
            "payment_method": "wallet" | "stripe" | "manual",
            "discount_code": "optional_discount_code"
        }
        """
        installment = self.get_object()
        
        # Validate client owns the order
        if installment.special_order.client != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to pay for this installment.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        payment_method = request.data.get('payment_method', 'wallet')
        discount_code = request.data.get('discount_code')
        
        try:
            payment = SpecialOrderInstallmentPaymentService.process_installment_payment(
                installment=installment,
                client=request.user,
                payment_method=payment_method,
                discount_code=discount_code
            )
            
            return Response({
                'status': 'success',
                'payment_id': payment.id,
                'payment_status': payment.status,
                'installment_id': installment.id,
                'amount': float(payment.amount),
                'message': 'Installment payment processed successfully.'
            }, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception(f"Error processing installment payment: {e}")
            return Response(
                {'error': 'An error occurred processing the payment.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
    Admins can create/manage, writers can view their own.
    """
    queryset = WriterBonus.objects.select_related(
        'writer', 'special_order', 'website'
    )
    serializer_class = WriterBonusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter bonuses by writer or return all for admin.
        """
        user = self.request.user
        if user.is_staff or getattr(user, 'role', None) in ['admin', 'superadmin', 'support']:
            return WriterBonus.objects.all()
        elif getattr(user, 'role', None) == 'writer':
            return WriterBonus.objects.filter(writer=user)
        return WriterBonus.objects.none()
    
    def get_permissions(self):
        """
        Admins can create/update/delete, writers can only view.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """
        Save writer bonus using streamlined service if add_to_wallet is requested.
        """
        add_to_wallet = self.request.data.get('add_to_wallet', False)
        
        if add_to_wallet:
            # Use streamlined service
            from writer_management.services.writer_payment_award_service import WriterPaymentAwardService
            from websites.utils import get_current_website
            
            writer_id = serializer.validated_data.get('writer').id
            amount = serializer.validated_data.get('amount')
            category = serializer.validated_data.get('category', 'other')
            reason = serializer.validated_data.get('reason', '')
            special_order = serializer.validated_data.get('special_order')
            website = get_current_website(self.request) or serializer.validated_data.get('website')
            
            try:
                result = WriterPaymentAwardService.award_bonus(
                    writer_id=writer_id,
                    amount=amount,
                    category=category,
                    reason=reason,
                    special_order_id=special_order.id if special_order else None,
                    add_to_wallet=True,
                    website=website,
                    admin_user=self.request.user
                )
                # Return the created bonus
                bonus = WriterBonus.objects.get(id=result['bonus_id'])
                serializer.instance = bonus
            except Exception as e:
                logger.exception(f"Error creating bonus with wallet: {e}")
                # Fallback to regular creation
                serializer.save()
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def pay(self, request, pk=None):
        """
        Mark bonus as paid and optionally add to wallet (streamlined).
        
        Request body:
        {
            "add_to_wallet": true  // If true, add to writer's wallet
        }
        """
        bonus = self.get_object()
        add_to_wallet = request.data.get('add_to_wallet', True)
        
        from writer_management.services.writer_payment_award_service import WriterPaymentAwardService
        from websites.utils import get_current_website
        
        website = get_current_website(request) or bonus.website
        
        try:
            result = WriterPaymentAwardService.pay_bonus(
                bonus_id=bonus.id,
                add_to_wallet=add_to_wallet,
                website=website,
                admin_user=request.user
            )
            serializer = WriterBonusSerializer(bonus)
            return Response({
                'bonus': serializer.data,
                'added_to_wallet': result['added_to_wallet'],
                'wallet_balance': result.get('wallet_balance'),
            })
        except Exception as e:
            logger.exception(f"Error paying bonus: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class EstimatedSpecialOrderSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Estimated Special Order deposit settings.
    """
    queryset = EstimatedSpecialOrderSettings.objects.all()
    serializer_class = EstimatedSpecialOrderSettingsSerializer
    permission_classes = [IsAdminUser]

