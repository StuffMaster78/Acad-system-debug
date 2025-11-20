"""
Service for processing special order installment payments via OrderPayment infrastructure.
"""

import logging
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from special_orders.models import SpecialOrder, InstallmentPayment
from order_payments_management.models import OrderPayment
from order_payments_management.services.payment_service import OrderPaymentService

logger = logging.getLogger(__name__)


class SpecialOrderInstallmentPaymentService:
    """
    Service for processing special order installment payments.
    Integrates with OrderPayment to provide unified payment processing.
    """

    @staticmethod
    @transaction.atomic
    def process_installment_payment(
        installment: InstallmentPayment,
        client,
        payment_method: str = 'wallet',
        discount_code: str = None
    ) -> OrderPayment:
        """
        Process payment for a special order installment.
        
        Creates OrderPayment record, processes payment (wallet/gateway),
        and links it to the installment.
        
        Args:
            installment: InstallmentPayment instance to pay
            client: Client making the payment
            payment_method: 'wallet', 'stripe', 'manual', etc.
            discount_code: Optional discount code (applies to installment amount)
            
        Returns:
            OrderPayment: Created payment record
            
        Raises:
            ValidationError: If installment already paid or validation fails
        """
        if installment.is_paid:
            raise ValidationError("This installment has already been paid.")
        
        special_order = installment.special_order
        
        # Validate client owns the order
        if special_order.client != client:
            raise ValidationError("You do not have permission to pay for this installment.")
        
        # Determine payment_type based on special order type
        if special_order.order_type == 'predefined':
            payment_type = 'predefined_special'
        elif special_order.order_type == 'estimated':
            payment_type = 'estimated_special'
        else:
            payment_type = 'special_installment'  # Fallback
        
        # Apply discount if provided (note: discounts typically apply to order total,
        # but can apply to individual installments if needed)
        original_amount = installment.amount_due
        discounted_amount = original_amount
        
        # TODO: Implement discount application for installments if needed
        # For now, discounts should apply at order level before installments are generated
        
        # Create OrderPayment record for the installment
        payment = OrderPayment.objects.create(
            client=client,
            website=special_order.website,
            payment_type=payment_type,
            special_order=special_order,
            order=None,  # No standard order
            class_purchase=None,  # No class purchase
            amount=original_amount,
            original_amount=original_amount,
            discounted_amount=discounted_amount,
            discount=None,  # Discounts applied at order level
            status='pending',
            payment_method=payment_method,
            related_object_id=installment.id,
            related_object_type='installment_payment',
        )
        
        logger.info(
            f"Created OrderPayment {payment.id} for installment {installment.id} "
            f"(special order #{special_order.id})"
        )
        
        # Process payment based on method
        if payment_method == 'wallet':
            try:
                payment = OrderPaymentService.process_wallet_payment(payment)
            except ValueError as e:
                logger.error(f"Wallet payment failed for installment {installment.id}: {e}")
                raise ValidationError(f"Payment failed: {str(e)}")
        elif payment_method in ['stripe', 'paypal']:
            # Future: Gateway integration
            # For now, mark as pending for manual confirmation
            payment = OrderPaymentService.mark_as_external_pending(payment)
        elif payment_method == 'manual':
            # Admin will confirm manually
            payment.status = 'pending'
            payment.save()
        
        # Link payment to installment and mark as paid
        if payment.status == 'completed':
            installment.mark_paid(payment_record=payment)
            
            # Check if all installments are paid
            SpecialOrderInstallmentPaymentService._check_all_installments_paid(special_order)
        
        return payment
    
    @staticmethod
    def _check_all_installments_paid(special_order: SpecialOrder):
        """
        Check if all installments are paid and update special order status.
        
        Args:
            special_order: SpecialOrder instance to check
        """
        unpaid_count = special_order.installments.filter(is_paid=False).count()
        
        if unpaid_count == 0:
            # All installments paid
            if special_order.status == 'awaiting_approval':
                special_order.status = 'in_progress'
                special_order.save()
                logger.info(
                    f"All installments paid for special order #{special_order.id}. "
                    f"Status updated to 'in_progress'."
                )
    
    @staticmethod
    @transaction.atomic
    def refund_installment_payment(
        installment: InstallmentPayment,
        refund_amount: Decimal = None,
        refund_method: str = 'wallet',
        reason: str = None
    ):
        """
        Refund an installment payment.
        
        Args:
            installment: InstallmentPayment to refund
            refund_amount: Amount to refund (defaults to full installment amount)
            refund_method: 'wallet' or 'external'
            reason: Refund reason
            
        Returns:
            Refund: Created refund record
        """
        if not installment.has_payment_record:
            raise ValidationError("Installment does not have a payment record to refund.")
        
        payment = installment.payment_record
        
        if refund_amount is None:
            refund_amount = payment.discounted_amount
        
        # Use OrderPayment refund system
        from order_payments_management.models import Refund
        
        refund = Refund.objects.create(
            payment=payment,
            client=payment.client,
            website=payment.website,
            amount=refund_amount,
            refund_method=refund_method,
            status='pending',
            refund_reason=reason
        )
        
        logger.info(
            f"Created refund {refund.id} for installment {installment.id} "
            f"(payment {payment.id})"
        )
        
        return refund

