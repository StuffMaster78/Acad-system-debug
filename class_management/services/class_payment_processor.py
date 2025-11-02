"""
Service for processing class bundle payments (deposits and installments)
via the unified OrderPayment workflow.
"""

import logging
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from class_management.models import ClassBundle, ClassInstallment, ClassPurchase
from order_payments_management.models import OrderPayment
from order_payments_management.services.payment_service import OrderPaymentService
from order_payments_management.services.unified_payment_service import UnifiedPaymentService
from notifications_system.services.notification_helper import NotificationHelper

logger = logging.getLogger(__name__)


class ClassPaymentProcessor:
    """
    Service for processing class bundle payments.
    Integrates with OrderPayment to provide unified payment processing.
    """
    
    @staticmethod
    @transaction.atomic
    def process_deposit_payment(
        bundle: ClassBundle,
        client,
        payment_method: str = 'wallet',
        discount_code: str = None
    ) -> OrderPayment:
        """
        Process deposit payment for a class bundle.
        
        Args:
            bundle: ClassBundle instance
            client: Client making the payment
            payment_method: 'wallet', 'stripe', 'manual', etc.
            discount_code: Optional discount code (applies to deposit)
            
        Returns:
            OrderPayment: Created payment record
            
        Raises:
            ValidationError: If deposit already paid or validation fails
        """
        if bundle.has_deposit_paid:
            raise ValidationError("Deposit for this bundle has already been paid.")
        
        if bundle.deposit_required <= 0:
            raise ValidationError("No deposit required for this bundle.")
        
        # Apply discount if provided (note: discounts typically apply to total, not deposit)
        # For now, we'll allow discount on deposit if specified
        original_amount = bundle.deposit_required
        discounted_amount = original_amount
        
        # TODO: Implement discount application for deposits if needed
        # For now, discounts should apply at bundle level before deposit is calculated
        
        # Create OrderPayment record for the deposit
        # Note: We'll link class_purchase after creating both records
        payment = UnifiedPaymentService.create_payment(
            payment_type='class_payment',
            client=client,
            website=bundle.website,
            amount=original_amount,
            original_amount=original_amount,
            discounted_amount=discounted_amount,
            payment_method=payment_method,
            order=None,
            special_order=None,
            class_purchase=None,  # Will be set after creating ClassPurchase
            installment_payment=None,
            related_object_id=bundle.id,
            related_object_type='class_bundle_deposit',
        )
        
        # Create ClassPurchase record for tracking
        class_purchase = ClassPurchase.objects.create(
            client=client,
            bundle=bundle,
            website=bundle.website,
            payment_record=payment,
            payment_type='deposit',
            status='pending',
            price_locked=original_amount,
        )
        
        # Link OrderPayment to ClassPurchase
        payment.class_purchase = class_purchase
        payment.save(update_fields=['class_purchase'])
        
        logger.info(
            f"Created deposit payment {payment.id} for bundle {bundle.id} "
            f"(amount: ${original_amount})"
        )
        
        # Process payment based on method
        if payment_method == 'wallet':
            try:
                payment = OrderPaymentService.process_wallet_payment(payment)
            except ValueError as e:
                logger.error(f"Wallet payment failed for bundle {bundle.id}: {e}")
                raise ValidationError(f"Payment failed: {str(e)}")
        elif payment_method in ['stripe', 'paypal']:
            # Future: Gateway integration
            payment = OrderPaymentService.mark_as_external_pending(payment)
        elif payment_method == 'manual':
            # Admin will confirm manually
            payment.status = 'pending'
            payment.save()
        
        # Update bundle if payment completed
        if payment.status == 'completed':
            ClassPaymentProcessor._update_bundle_after_deposit(bundle, payment, class_purchase)
            
            # Send notification
            try:
                NotificationHelper.notify_class_deposit_paid(
                    class_bundle=bundle,
                    amount=payment.discounted_amount or payment.amount,
                    balance_remaining=bundle.balance_remaining
                )
            except Exception as e:
                logger.error(f"Failed to send deposit paid notification: {e}")
        
        return payment
    
    @staticmethod
    @transaction.atomic
    def process_installment_payment(
        installment: ClassInstallment,
        client,
        payment_method: str = 'wallet',
        discount_code: str = None
    ) -> OrderPayment:
        """
        Process payment for a class bundle installment.
        
        Args:
            installment: ClassInstallment instance to pay
            client: Client making the payment
            payment_method: 'wallet', 'stripe', 'manual', etc.
            discount_code: Optional discount code
            
        Returns:
            OrderPayment: Created payment record
            
        Raises:
            ValidationError: If installment already paid or validation fails
        """
        if installment.is_paid:
            raise ValidationError("This installment has already been paid.")
        
        bundle = installment.class_bundle
        
        # Validate client owns the bundle
        if bundle.client != client:
            raise ValidationError("You do not have permission to pay for this installment.")
        
        # Ensure deposit is paid first
        if not bundle.has_deposit_paid:
            raise ValidationError("Deposit must be paid before paying installments.")
        
        original_amount = installment.amount
        discounted_amount = original_amount
        
        # Create OrderPayment record for the installment
        payment = UnifiedPaymentService.create_payment(
            payment_type='class_payment',
            client=client,
            website=bundle.website,
            amount=original_amount,
            original_amount=original_amount,
            discounted_amount=discounted_amount,
            payment_method=payment_method,
            order=None,
            special_order=None,
            class_purchase=None,
            installment_payment=None,
            related_object_id=installment.id,
            related_object_type='class_installment',
        )
        
        logger.info(
            f"Created installment payment {payment.id} for installment {installment.id} "
            f"(bundle {bundle.id}, amount: ${original_amount})"
        )
        
        # Process payment based on method
        if payment_method == 'wallet':
            try:
                payment = OrderPaymentService.process_wallet_payment(payment)
            except ValueError as e:
                logger.error(f"Wallet payment failed for installment {installment.id}: {e}")
                raise ValidationError(f"Payment failed: {str(e)}")
        elif payment_method in ['stripe', 'paypal']:
            payment = OrderPaymentService.mark_as_external_pending(payment)
        elif payment_method == 'manual':
            payment.status = 'pending'
            payment.save()
        
        # Link payment to installment and mark as paid
        if payment.status == 'completed':
            installment.mark_paid(payment_record=payment, paid_by=client)
            
            # Check if all installments are paid
            ClassPaymentProcessor._check_all_installments_paid(bundle)
            
            # Notify if bundle is fully paid
            if bundle.is_fully_paid:
                try:
                    NotificationHelper.send_notification(
                        user=client,
                        event="class.bundle.completed",
                        payload={
                            "bundle_id": bundle.id,
                            "bundle_name": f"Class Bundle #{bundle.id}",
                            "number_of_classes": bundle.number_of_classes or 1,
                            "website_id": bundle.website_id
                        },
                        website=bundle.website
                    )
                except Exception as e:
                    logger.error(f"Failed to send bundle completed notification: {e}")
        
        return payment
    
    @staticmethod
    def _update_bundle_after_deposit(bundle: ClassBundle, payment: OrderPayment, class_purchase: ClassPurchase):
        """Update bundle after deposit payment is completed."""
        bundle.deposit_paid = payment.discounted_amount
        bundle.save()
        
        class_purchase.status = 'paid'
        class_purchase.paid_at = timezone.now()
        class_purchase.save()
        
        logger.info(
            f"Deposit payment completed for bundle {bundle.id}. "
            f"Deposit paid: ${bundle.deposit_paid}"
        )
    
    @staticmethod
    def _check_all_installments_paid(bundle: ClassBundle):
        """
        Check if all installments are paid and update bundle status if needed.
        
        Args:
            bundle: ClassBundle instance to check
        """
        unpaid_count = bundle.installments.filter(is_paid=False).count()
        
        if unpaid_count == 0 and bundle.installments_enabled:
            logger.info(
                f"All installments paid for bundle {bundle.id}. "
                f"Bundle is fully paid: {bundle.is_fully_paid}"
            )
    
    @staticmethod
    @transaction.atomic
    def process_full_payment(
        bundle: ClassBundle,
        client,
        payment_method: str = 'wallet',
        discount_code: str = None
    ) -> OrderPayment:
        """
        Process full payment for a class bundle (no installments).
        
        Args:
            bundle: ClassBundle instance
            client: Client making the payment
            payment_method: 'wallet', 'stripe', 'manual', etc.
            discount_code: Optional discount code
            
        Returns:
            OrderPayment: Created payment record
        """
        if bundle.is_fully_paid:
            raise ValidationError("This bundle has already been fully paid.")
        
        # Calculate amount to pay (total - deposit already paid)
        amount_due = bundle.total_price - bundle.deposit_paid
        
        if amount_due <= 0:
            raise ValidationError("No balance remaining to pay.")
        
        original_amount = amount_due
        discounted_amount = original_amount
        
        # Create OrderPayment record
        payment = UnifiedPaymentService.create_payment(
            payment_type='class_payment',
            client=client,
            website=bundle.website,
            amount=original_amount,
            original_amount=original_amount,
            discounted_amount=discounted_amount,
            payment_method=payment_method,
            order=None,
            special_order=None,
            class_purchase=None,
            installment_payment=None,
            related_object_id=bundle.id,
            related_object_type='class_bundle_full',
        )
        
        # Create ClassPurchase record
        class_purchase = ClassPurchase.objects.create(
            client=client,
            bundle=bundle,
            website=bundle.website,
            payment_record=payment,
            payment_type='full',
            status='pending',
            price_locked=original_amount,
        )
        
        logger.info(
            f"Created full payment {payment.id} for bundle {bundle.id} "
            f"(amount: ${original_amount})"
        )
        
        # Process payment
        if payment_method == 'wallet':
            try:
                payment = OrderPaymentService.process_wallet_payment(payment)
            except ValueError as e:
                logger.error(f"Wallet payment failed for bundle {bundle.id}: {e}")
                raise ValidationError(f"Payment failed: {str(e)}")
        elif payment_method in ['stripe', 'paypal']:
            payment = OrderPaymentService.mark_as_external_pending(payment)
        
        # Update bundle if payment completed
        if payment.status == 'completed':
            # Mark bundle as fully paid
            bundle.update_balance()
            class_purchase.status = 'paid'
            class_purchase.paid_at = timezone.now()
            class_purchase.save()
        
        return payment

