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
    'smart',  # Smart payment: wallet → points → gateway
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
    def process_smart_payment(
        payment: OrderPayment,
        external_gateway: str = 'stripe',
        external_id: str = None
    ) -> dict:
        """
        Process smart payment that automatically uses:
        1. Wallet balance first
        2. Loyalty points (converted to wallet) second
        3. External payment gateway for remainder
        
        Args:
            payment: OrderPayment instance to process
            external_gateway: Gateway to use for remainder ('stripe', 'paypal', etc.)
            external_id: Optional external payment ID if already initiated
            
        Returns:
            dict: {
                'status': 'completed' | 'pending',
                'wallet_amount': Decimal,
                'points_used': int,
                'points_amount': Decimal,
                'gateway_amount': Decimal,
                'split_payments': list of SplitPayment records
            }
            
        Raises:
            ValueError: If payment cannot be completed
        """
        from wallet.models import Wallet
        from client_management.models import ClientProfile
        from loyalty_management.services.loyalty_conversion_service import LoyaltyConversionService
        from loyalty_management.models import LoyaltyPointsConversionConfig
        from ..models import SplitPayment
        import logging
        
        logger = logging.getLogger(__name__)
        
        total_amount = payment.discounted_amount or payment.amount
        remaining = total_amount
        split_payments_data = []
        
        # Step 1: Use wallet balance first
        # Get or create wallet, then lock it
        wallet, created = Wallet.objects.get_or_create(
            user=payment.client,
            website=payment.website,
            defaults={'balance': Decimal('0.00')}
        )
        # Lock the wallet for update
        wallet = Wallet.objects.select_for_update().get(id=wallet.id)
        wallet_amount = min(wallet.balance, remaining)
        
        if wallet_amount > 0:
            wallet.balance -= wallet_amount
            wallet.save(update_fields=['balance'])
            remaining -= wallet_amount
            split_payments_data.append({
                'method': 'wallet',
                'amount': wallet_amount
            })
            logger.info(f"Smart payment: Used ${wallet_amount} from wallet for payment {payment.id}")
        
        # Step 2: Convert and use loyalty points if still needed
        points_used = 0
        points_amount = Decimal('0.00')
        
        if remaining > 0:
            try:
                client_profile = ClientProfile.objects.get(user=payment.client, website=payment.website)
                total_points = LoyaltyConversionService.get_total_points(client_profile)
                
                if total_points > 0:
                    # Get conversion config
                    config = LoyaltyPointsConversionConfig.objects.filter(
                        website=payment.website,
                        active=True
                    ).first()
                    
                    if config and config.min_conversion_points > 0:
                        # Calculate how many points we need to cover remaining amount
                        # points_needed = remaining / conversion_rate
                        points_needed_decimal = remaining / config.conversion_rate
                        points_needed = int(points_needed_decimal)
                        
                        # Use available points (up to what we need)
                        points_to_use = min(total_points, points_needed)
                        
                        # Ensure we meet minimum conversion requirement
                        if points_to_use >= config.min_conversion_points:
                            # Convert points to wallet amount
                            points_amount = Decimal(points_to_use) * config.conversion_rate
                            
                            # If points amount exceeds remaining, adjust
                            if points_amount > remaining:
                                # Recalculate points needed for exact remaining amount
                                points_to_use = int(remaining / config.conversion_rate)
                                points_amount = Decimal(points_to_use) * config.conversion_rate
                            
                            # Deduct points and add to wallet
                            LoyaltyConversionService.deduct_points(
                                client_profile=client_profile,
                                points=points_to_use,
                                website=payment.website,
                                reason=f"Payment for Order {payment.order.id if payment.order else 'N/A'}"
                            )
                            
                            # Add converted amount to wallet
                            wallet.balance += points_amount
                            wallet.save(update_fields=['balance'])
                            
                            # Deduct from wallet for payment
                            wallet.balance -= points_amount
                            wallet.save(update_fields=['balance'])
                            
                            remaining -= points_amount
                            points_used = points_to_use
                            split_payments_data.append({
                                'method': 'loyalty_points',
                                'amount': points_amount,
                                'points': points_to_use
                            })
                            logger.info(f"Smart payment: Converted and used {points_to_use} points (${points_amount}) for payment {payment.id}")
            except ClientProfile.DoesNotExist:
                logger.warning(f"ClientProfile not found for user {payment.client.id}, skipping points")
            except Exception as e:
                logger.error(f"Error processing loyalty points for payment {payment.id}: {e}", exc_info=True)
                # Continue with gateway payment even if points conversion fails
        
        # Step 3: Use external payment gateway for remainder
        gateway_amount = Decimal('0.00')
        if remaining > 0:
            gateway_amount = remaining
            # Mark payment as pending external processing
            payment.status = 'pending'
            payment.payment_method = external_gateway
            if external_id:
                payment.external_id = external_id
            payment.save()
            
            split_payments_data.append({
                'method': external_gateway,
                'amount': gateway_amount
            })
            logger.info(f"Smart payment: Remaining ${gateway_amount} to be paid via {external_gateway} for payment {payment.id}")
        else:
            # All paid, mark as completed
            payment.status = 'completed'
            payment.confirmed_at = timezone.now()
            payment.save()
            
            # Send notification
            if payment.order and payment.order.client:
                try:
                    NotificationHelper.notify_order_paid(
                        order=payment.order,
                        payment_amount=total_amount,
                        payment_method='smart_payment'
                    )
                except Exception as e:
                    logger.error(f"Failed to send payment completed notification: {e}")
        
        # Create SplitPayment records for tracking
        split_payments = []
        for split_data in split_payments_data:
            split_payment = SplitPayment.objects.create(
                payment=payment,
                website=payment.website,
                method=split_data['method'],
                amount=split_data['amount']
            )
            split_payments.append(split_payment)
        
        return {
            'status': 'completed' if remaining == 0 else 'pending',
            'wallet_amount': wallet_amount,
            'points_used': points_used,
            'points_amount': points_amount,
            'gateway_amount': gateway_amount,
            'split_payments': split_payments,
            'total_paid': wallet_amount + points_amount + gateway_amount,
            'remaining': remaining
        }

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
