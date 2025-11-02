"""
Unified payment service supporting all payment types:
- Standard orders
- Special orders (predefined and estimated)
- Special order installments
- Class purchases
- Wallet loading
"""

import logging
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..models import OrderPayment

logger = logging.getLogger(__name__)


class UnifiedPaymentService:
    """
    Unified service for creating payments across all payment types.
    Provides proper identification via payment_type and related FKs.
    """
    
    @staticmethod
    @transaction.atomic
    def create_payment(
        payment_type: str,
        client,
        website,
        amount: Decimal,
        payment_method: str = 'wallet',
        order=None,
        special_order=None,
        class_purchase=None,
        installment_payment=None,
        discount_code: str = None,
        original_amount: Decimal = None,
        **kwargs
    ) -> OrderPayment:
        """
        Create a payment record for any payment type.
        
        Args:
            payment_type: One of PAYMENT_TYPE_CHOICES
            client: Client making the payment
            website: Website context
            amount: Payment amount
            payment_method: 'wallet', 'stripe', 'manual', etc.
            order: Order instance (for 'standard' type)
            special_order: SpecialOrder instance (for special order types)
            class_purchase: ClassPurchase instance (for 'class_payment' type)
            installment_payment: InstallmentPayment instance (for 'special_installment' type)
            discount_code: Optional discount code
            original_amount: Original amount before discount
            **kwargs: Additional fields for OrderPayment
            
        Returns:
            OrderPayment: Created payment instance
            
        Raises:
            ValidationError: If payment type and related objects don't match
        """
        # Validate payment type and required relationships
        UnifiedPaymentService._validate_payment_type_and_relationships(
            payment_type, order, special_order, class_purchase, installment_payment
        )
        
        if original_amount is None:
            original_amount = amount
        
        discounted_amount = amount
        
        # Apply discounts (only for orders and special orders, not installments)
        discount = None
        if payment_type in ['standard', 'predefined_special', 'estimated_special']:
            # Discounts handled separately via DiscountEngine
            # For now, just set amounts
            discounted_amount = amount
        
        # Determine related_object fields for installments
        related_object_id = None
        related_object_type = None
        if installment_payment:
            related_object_id = installment_payment.id
            related_object_type = 'installment_payment'
        
        # Create payment record
        payment = OrderPayment.objects.create(
            payment_type=payment_type,
            client=client,
            website=website,
            order=order,
            special_order=special_order,
            class_purchase=class_purchase,
            amount=amount,
            original_amount=original_amount,
            discounted_amount=discounted_amount,
            discount=discount,
            status='pending',
            payment_method=payment_method,
            related_object_id=related_object_id,
            related_object_type=related_object_type,
            **kwargs
        )
        
        logger.info(
            f"Created {payment_type} payment {payment.id} for client {client.id} "
            f"(amount: ${amount})"
        )
        
        return payment
    
    @staticmethod
    def _validate_payment_type_and_relationships(
        payment_type: str,
        order,
        special_order,
        class_purchase,
        installment_payment
    ):
        """Validate that payment_type matches provided relationships."""
        if payment_type == 'standard' and not order:
            raise ValidationError("Standard payments require an order.")
        elif payment_type == 'standard' and (special_order or class_purchase):
            raise ValidationError("Standard payments cannot have special_order or class_purchase.")
        
        elif payment_type in ['predefined_special', 'estimated_special'] and not special_order:
            raise ValidationError(f"{payment_type} payments require a special_order.")
        elif payment_type in ['predefined_special', 'estimated_special'] and (order or class_purchase):
            raise ValidationError(f"{payment_type} payments cannot have order or class_purchase.")
        
        elif payment_type == 'special_installment' and not installment_payment:
            raise ValidationError("Special installment payments require an installment_payment.")
        elif payment_type == 'special_installment' and not installment_payment.special_order:
            raise ValidationError("Installment payment must be linked to a special_order.")
        
        elif payment_type == 'class_payment' and not class_purchase:
            raise ValidationError("Class payments require a class_purchase.")
        elif payment_type == 'class_payment' and (order or special_order):
            raise ValidationError("Class payments cannot have order or special_order.")
        
        elif payment_type == 'wallet_loading':
            # Wallet loading doesn't require order relationships
            if order or special_order or class_purchase:
                raise ValidationError("Wallet loading payments should not have order relationships.")
    
    @staticmethod
    @transaction.atomic
    def create_wallet_loading_payment(
        client,
        website,
        amount: Decimal,
        payment_method: str = 'stripe',
        external_id: str = None
    ) -> OrderPayment:
        """
        Create a payment record for wallet loading/top-up.
        
        Args:
            client: Client loading wallet
            website: Website context
            amount: Amount to load
            payment_method: Payment method (typically 'stripe', 'paypal', etc.)
            external_id: External payment ID (if already created)
            
        Returns:
            OrderPayment: Created payment record
        """
        payment = UnifiedPaymentService.create_payment(
            payment_type='wallet_loading',
            client=client,
            website=website,
            amount=amount,
            original_amount=amount,
            discounted_amount=amount,
            payment_method=payment_method,
            order=None,
            special_order=None,
            class_purchase=None,
            installment_payment=None,
        )
        
        if external_id:
            payment.stripe_payment_intent_id = external_id
            payment.save()
        
        logger.info(
            f"Created wallet loading payment {payment.id} for client {client.id} "
            f"(amount: ${amount})"
        )
        
        return payment
    
    @staticmethod
    @transaction.atomic
    def confirm_wallet_loading_payment(
        payment: OrderPayment,
        external_id: str = None
    ) -> OrderPayment:
        """
        Confirm a wallet loading payment and credit the wallet.
        
        Args:
            payment: OrderPayment instance (wallet_loading type)
            external_id: External payment ID
            
        Returns:
            OrderPayment: Updated payment
        """
        if payment.payment_type != 'wallet_loading':
            raise ValidationError("Payment must be of type 'wallet_loading'.")
        
        if payment.status == 'completed':
            raise ValidationError("Payment is already completed.")
        
        from wallet.models import Wallet
        
        # Credit wallet
        wallet = Wallet.objects.select_for_update().get(user=payment.client)
        wallet.balance += payment.discounted_amount
        wallet.save()
        
        # Mark payment as completed
        payment.status = 'completed'
        payment.confirmed_at = timezone.now()
        if external_id:
            payment.stripe_payment_intent_id = external_id
        payment.save()
        
        logger.info(
            f"Wallet loading payment {payment.id} confirmed. "
            f"Credited ${payment.discounted_amount} to wallet."
        )
        
        return payment

