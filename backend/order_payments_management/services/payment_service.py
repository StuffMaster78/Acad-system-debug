"""
Payment service for handling order payments.

This service handles payment creation and processing.
Gateway integration will be added later - for now it supports:
- Wallet payments (immediate)
- Manual admin payments (external processors)
- Payment record creation for future gateway integration
"""

from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..models import OrderPayment
from orders.models import Order
from discounts.models.discount import Discount
from notifications_system.services.notification_helper import NotificationHelper

# Valid payment methods
VALID_PAYMENT_METHODS = [
    'wallet',
    'manual',  # Admin-processed external payment
    'stripe',  # Future: Stripe integration
    'paypal',  # Future: PayPal integration
    'credit_card',  # Future: Direct credit card
    'bank_transfer',  # Future: Bank transfer
]


class OrderPaymentService:
    """
    Service for handling order payment operations.
    
    Note: Gateway integration (Stripe/PayPal) will be added later.
    For now, supports wallet payments and manual payment record creation.
    """

    @staticmethod
    @transaction.atomic
    def create_payment(
        order: Order,
        client,
        payment_method: str,
        amount: Decimal = None,
        discount_code: str = None,
        original_amount: Decimal = None,
    ) -> OrderPayment:
        """
        Create a payment record for an order.
        
        Args:
            order: The order being paid for
            client: The client making the payment
            payment_method: Payment method ('wallet', 'stripe', 'manual', etc.)
            amount: Payment amount (defaults to order.total_price)
            discount_code: Optional discount code to apply
            original_amount: Original amount before discount
            
        Returns:
            OrderPayment: Created payment instance with status='pending'
        """
        # Validate payment method
        if payment_method not in VALID_PAYMENT_METHODS:
            raise ValidationError(
                f"Invalid payment method '{payment_method}'. "
                f"Valid methods: {', '.join(VALID_PAYMENT_METHODS)}"
            )
        
        # Use order total if amount not specified
        if amount is None:
            amount = order.total_price
        
        if original_amount is None:
            original_amount = amount
        
        discounted_amount = amount
        discount = None
        
        # Use DiscountEngine for proper discount application with stacking, validation, and caps
        # This ensures all business rules are enforced
        from discounts.services.discount_engine import DiscountEngine
        
        discount_codes_to_apply = []
        
        # If order already has discount applied, include it
        if order.discount:
            discount_codes_to_apply.append(order.discount.discount_code)
        
        # If discount code provided, add it (will be validated by DiscountEngine)
        if discount_code:
            discount_codes_to_apply.append(discount_code)
        
        # Apply discounts using DiscountEngine (handles stacking, caps, validation)
        if discount_codes_to_apply:
            try:
                final_price, applied_discounts_list = DiscountEngine.apply_discount_to_order(
                    order=order,
                    codes=discount_codes_to_apply,
                    website=order.website,
                    user=client
                )
                discounted_amount = final_price
                
                # Get the primary discount for tracking (use the first one if multiple)
                if applied_discounts_list:
                    # Find the discount object from the applied list
                    primary_discount_code = applied_discounts_list[0]['code']
                    discount = Discount.objects.filter(
                        discount_code=primary_discount_code,
                        website=order.website
                    ).first()
                elif order.discount:
                    discount = order.discount
                else:
                    discount = None
            except ValidationError as e:
                raise ValidationError(f"Discount application failed: {str(e)}")
        else:
            # No discounts to apply
            discounted_amount = original_amount
            discount = None
        
        # Create payment record
        payment = OrderPayment.objects.create(
            order=order,
            client=client,
            website=order.website,
            payment_type="standard",
            amount=amount,
            original_amount=original_amount,
            discounted_amount=discounted_amount,
            discount=discount,
            status="pending",
            payment_method=payment_method,
        )
        
        # Note: Discount usage is tracked by DiscountEngine.apply_discount_to_order()
        # via DiscountUsageTracker.track_multiple(), so no need to increment here
        
        return payment

    @staticmethod
    @transaction.atomic
    def process_wallet_payment(payment: OrderPayment) -> OrderPayment:
        """
        Process payment using client's wallet balance.
        
        Args:
            payment: OrderPayment instance to process
            
        Returns:
            OrderPayment: Updated payment with status='completed'
            
        Raises:
            ValueError: If insufficient wallet balance
        """
        from wallet.models import Wallet
        
        # Lock wallet row for atomic operation
        wallet = Wallet.objects.select_for_update().get(user=payment.client)
        
        if wallet.balance < payment.discounted_amount:
            raise ValueError("Insufficient wallet balance.")
        
        # Deduct from wallet
        wallet.balance -= payment.discounted_amount
        wallet.save()
        
        # Mark payment as completed
        payment.status = 'completed'
        payment.confirmed_at = timezone.now()
        payment.save()
        
        return payment

    @staticmethod
    def mark_as_external_pending(payment: OrderPayment, external_id: str = None) -> OrderPayment:
        """
        Mark payment as pending external processing.
        
        This is used when payment will be processed via gateway/webhook later.
        The payment is made on an external payment gateway website, which will
        send a webhook to confirm the payment on the client website.
        
        Args:
            payment: OrderPayment instance
            external_id: External payment ID (e.g., Stripe PaymentIntent ID, PayPal transaction ID)
            
        Returns:
            OrderPayment: Updated payment
        """
        payment.status = 'pending'
        if external_id:
            # Store external_id for webhook lookup
            payment.external_id = external_id
            # Also store in stripe_payment_intent_id if it looks like a Stripe ID
            if external_id.startswith('pi_'):
                payment.stripe_payment_intent_id = external_id
        payment.save()
        return payment

    @staticmethod
    @transaction.atomic
    def confirm_external_payment(
        payment: OrderPayment,
        external_id: str,
        raw_response: dict = None
    ) -> OrderPayment:
        """
        Confirm an external payment (called by webhook/future gateway integration).
        
        Args:
            payment: OrderPayment instance
            external_id: External payment ID
            raw_response: Raw response from payment gateway
            
        Returns:
            OrderPayment: Updated payment with status='completed'
        """
        payment.status = 'completed'
        payment.external_id = external_id
        payment.confirmed_at = timezone.now()
        if raw_response:
            payment.raw_response = raw_response
        payment.save()
        
        # Send notification
        if payment.order and payment.order.client:
            try:
                NotificationHelper.notify_order_paid(
                    order=payment.order,
                    payment_amount=payment.discounted_amount or payment.amount,
                    payment_method=payment.payment_method or "payment method"
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send payment completed notification: {e}")
        
        return payment

    @staticmethod
    @transaction.atomic
    def mark_as_failed(payment: OrderPayment, reason: str = None) -> OrderPayment:
        """
        Mark payment as failed.
        
        Args:
            payment: OrderPayment instance
            reason: Failure reason
            
        Returns:
            OrderPayment: Updated payment with status='failed'
        """
        from ..models import FailedPayment
        
        payment.status = 'failed'
        payment.save()
        
        # Log failed payment
        FailedPayment.objects.create(
            payment=payment,
            client=payment.client,
            website=payment.website,
            failure_reason=reason or "Payment failed",
            retry_count=0
        )
        
        # Send notification
        if payment.order and payment.order.client:
            try:
                NotificationHelper.notify_payment_failed(
                    order=payment.order,
                    amount=payment.amount,
                    reason=reason or "Payment could not be processed"
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send payment failed notification: {e}")
        
        return payment
