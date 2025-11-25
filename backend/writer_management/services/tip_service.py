from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from writer_management.models.levels import WriterLevel
from writer_management.models.tipping import Tip
from writer_management.models.profile import WriterProfile


class TipService:
    """
    Service for handling tips and their distribution between writers and the platform.
    Supports direct tips, order-based tips, and class/task-based tips.
    """
    DEFAULT_WRITER_PERCENTAGE = Decimal("30.00")

    @classmethod
    def get_writer_level(cls, writer, website=None):
        """
        Get the writer's current level for tip percentage calculation.
        """
        try:
            profile = WriterProfile.objects.get(user=writer, website=website or writer.website)
            return profile.writer_level
        except WriterProfile.DoesNotExist:
            return None

    @classmethod
    def compute_split(cls, amount, writer_level=None):
        """
        Computes how much goes to the writer and how much to the platform.
        
        Args:
            amount: Total tip amount
            writer_level: WriterLevel instance with tip_percentage
            
        Returns:
            tuple: (percentage, writer_share, platform_profit)
        """
        if writer_level and writer_level.tip_percentage:
            pct = Decimal(str(writer_level.tip_percentage))
        else:
            pct = cls.DEFAULT_WRITER_PERCENTAGE

        writer_share = (amount * pct / Decimal("100.00")).quantize(Decimal("0.01"))
        platform_profit = (amount - writer_share).quantize(Decimal("0.01"))

        return pct, writer_share, platform_profit

    @classmethod
    def determine_tip_type(cls, order=None, related_entity_type=None, related_entity_id=None):
        """
        Determine tip type based on provided parameters.
        """
        if order:
            return 'order'
        elif related_entity_type and related_entity_id:
            return 'class'
        else:
            return 'direct'

    @classmethod
    @transaction.atomic
    def create_tip(
        cls, client, writer, amount,
        reason="", website=None, writer_level=None,
        order=None, related_entity_type=None, related_entity_id=None,
        origin="client"
    ):
        """
        Creates a tip and computes the split.
        
        Args:
            client: User who is sending the tip
            writer: User (writer) receiving the tip
            amount: Tip amount (Decimal or float)
            reason: Optional reason for the tip
            website: Website instance (for multitenancy)
            writer_level: WriterLevel instance (if None, fetched from writer profile)
            order: Order instance (for order-based tips)
            related_entity_type: Type of related entity (e.g., 'class_bundle', 'express_class')
            related_entity_id: ID of related entity
            origin: Origin of tip ('client', 'admin', 'system')
            
        Returns:
            Tip instance
        """
        # Validate amount
        if amount <= Decimal("0.00"):
            raise ValidationError("Tip amount must be greater than zero.")
        
        # Determine tip type
        tip_type = cls.determine_tip_type(order, related_entity_type, related_entity_id)
        
        # Validate tip type requirements
        if tip_type == 'order' and not order:
            raise ValidationError("Order is required for order-based tips.")
        if tip_type == 'class' and (not related_entity_type or not related_entity_id):
            raise ValidationError("Related entity type and ID are required for class-based tips.")
        
        # Get writer level if not provided
        if writer_level is None:
            writer_level = cls.get_writer_level(writer, website)
        
        # Compute split
        pct, writer_earning, platform_profit = cls.compute_split(
            Decimal(str(amount)), writer_level
        )
        
        # Create tip
        tip = Tip.objects.create(
            client=client,
            writer=writer,
            website=website or client.website,
            tip_type=tip_type,
            order=order,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            tip_amount=Decimal(str(amount)),
            tip_reason=reason,
            writer_level=writer_level,
            writer_percentage=pct,
            writer_earning=writer_earning,
            platform_profit=platform_profit,
            origin=origin,
            payment_status='pending',
        )
        
        return tip

    @classmethod
    @transaction.atomic
    def process_tip_payment(cls, tip, payment_method='wallet', discount_code=None):
        """
        Process payment for a tip.
        
        Args:
            tip: Tip instance
            payment_method: Payment method ('wallet', 'stripe', 'manual')
            discount_code: Optional discount code
            
        Returns:
            OrderPayment instance
        """
        from order_payments_management.services.unified_payment_service import UnifiedPaymentService
        
        # Create payment record
        payment = UnifiedPaymentService.create_tip_payment(
            tip=tip,
            client=tip.client,
            website=tip.website,
            amount=tip.tip_amount,
            payment_method=payment_method,
            discount_code=discount_code
        )
        
        # Link payment to tip
        tip.payment = payment
        tip.payment_status = 'processing'
        tip.save(update_fields=['payment', 'payment_status'])
        
        # Process payment
        if payment_method == 'wallet':
            from order_payments_management.services.payment_service import OrderPaymentService
            try:
                payment = OrderPaymentService.process_wallet_payment(payment)
            except Exception as e:
                tip.payment_status = 'failed'
                tip.save(update_fields=['payment_status'])
                raise
        
        # Update tip status based on payment status
        if payment.status == 'completed':
            tip.payment_status = 'completed'
        elif payment.status == 'failed':
            tip.payment_status = 'failed'
        tip.save(update_fields=['payment_status'])
        
        return payment