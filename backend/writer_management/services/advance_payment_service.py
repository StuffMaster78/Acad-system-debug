from decimal import Decimal
from django.db.models import Sum, Q, F
from django.utils.timezone import now
from orders.models import Order
from orders.order_enums import OrderStatus
from writer_management.services.earnings_calculator import WriterEarningsCalculator
from writer_management.models.advance_payment import WriterAdvancePaymentRequest, AdvanceDeduction
import logging

logger = logging.getLogger(__name__)

class AdvancePaymentService:
    """
    Service for handling advance payment requests and calculations.
    """
    
    # Default max advance percentage (can be configured per website/level)
    DEFAULT_MAX_ADVANCE_PERCENTAGE = Decimal('50.00')  # 50%
    
    # Risk adjustment factors for different order statuses
    RISK_FACTORS = {
        OrderStatus.IN_PROGRESS.value: Decimal('0.90'),  # 90% confidence
        OrderStatus.SUBMITTED.value: Decimal('0.95'),    # 95% confidence
        OrderStatus.UNDER_EDITING.value: Decimal('0.85'), # 85% confidence
        OrderStatus.REVIEWED.value: Decimal('0.98'),     # 98% confidence
        OrderStatus.COMPLETED.value: Decimal('1.00'),     # 100% confidence
    }
    
    @staticmethod
    def calculate_expected_earnings(writer, website, include_risk_adjustment=True):
        """
        Calculate expected earnings for a writer, accounting for order statuses
        that might affect payment (cancellations, revisions, etc.).
        
        Args:
            writer: WriterProfile instance
            website: Website instance
            include_risk_adjustment: Whether to apply risk factors based on order status
            
        Returns:
            Decimal: Expected earnings amount
        """
        if not writer.writer_level:
            return Decimal('0.00')
        
        # Get orders that are likely to result in payment
        # Exclude cancelled, refunded orders
        orders = Order.objects.filter(
            assigned_writer=writer.user,
            website=website,
            status__in=[
                OrderStatus.IN_PROGRESS.value,
                OrderStatus.SUBMITTED.value,
                OrderStatus.UNDER_EDITING.value,
                OrderStatus.REVIEWED.value,
                OrderStatus.COMPLETED.value,
            ]
        ).exclude(
            status__in=[
                OrderStatus.CANCELLED.value,
                OrderStatus.REFUNDED.value,
            ]
        )
        
        total_expected = Decimal('0.00')
        
        for order in orders:
            # Calculate base earnings for this order
            is_urgent = False
            if order.writer_deadline or order.client_deadline:
                deadline = order.writer_deadline or order.client_deadline
                hours_until = (deadline - now()).total_seconds() / 3600
                is_urgent = hours_until <= writer.writer_level.urgent_order_deadline_hours
            
            is_technical = getattr(order, 'is_technical', False) or \
                          (hasattr(order, 'subject') and getattr(order.subject, 'is_technical', False))
            
            base_earnings = WriterEarningsCalculator.calculate_earnings(
                writer.writer_level,
                order,
                is_urgent=is_urgent,
                is_technical=is_technical
            )
            
            # Apply risk adjustment if enabled
            if include_risk_adjustment:
                risk_factor = AdvancePaymentService.RISK_FACTORS.get(
                    order.status,
                    Decimal('0.80')  # Default 80% for unknown statuses
                )
                adjusted_earnings = base_earnings * risk_factor
            else:
                adjusted_earnings = base_earnings
            
            total_expected += adjusted_earnings
        
        # Subtract any outstanding advances
        outstanding_advances = AdvancePaymentService.get_outstanding_advances(writer, website)
        total_expected -= outstanding_advances
        
        return max(total_expected, Decimal('0.00'))
    
    @staticmethod
    def get_outstanding_advances(writer, website):
        """Get total outstanding advance amount for a writer"""
        outstanding_requests = WriterAdvancePaymentRequest.objects.filter(
            writer=writer,
            website=website,
            status__in=['approved', 'disbursed']
        )
        
        total = Decimal('0.00')
        for request in outstanding_requests:
            total += request.outstanding_amount
        
        return total
    
    @staticmethod
    def calculate_max_advance(writer, website, max_percentage=None):
        """
        Calculate maximum advance amount a writer can request.
        
        Args:
            writer: WriterProfile instance
            website: Website instance
            max_percentage: Maximum percentage of expected earnings (default from config)
            
        Returns:
            dict: {
                'expected_earnings': Decimal,
                'max_percentage': Decimal,
                'max_advance_amount': Decimal,
                'outstanding_advances': Decimal,
                'available_advance': Decimal
            }
        """
        if max_percentage is None:
            max_percentage = AdvancePaymentService.DEFAULT_MAX_ADVANCE_PERCENTAGE
        
        expected_earnings = AdvancePaymentService.calculate_expected_earnings(writer, website)
        outstanding_advances = AdvancePaymentService.get_outstanding_advances(writer, website)
        
        max_advance_amount = (expected_earnings * max_percentage) / Decimal('100.00')
        available_advance = max_advance_amount - outstanding_advances
        
        return {
            'expected_earnings': expected_earnings,
            'max_percentage': max_percentage,
            'max_advance_amount': max_advance_amount,
            'outstanding_advances': outstanding_advances,
            'available_advance': max(available_advance, Decimal('0.00'))
        }
    
    @staticmethod
    def deduct_from_payment(writer_payment, advance_request, amount):
        """
        Deduct advance repayment amount from a writer payment.
        
        Args:
            writer_payment: WriterPayment instance
            advance_request: WriterAdvancePaymentRequest instance
            amount: Amount to deduct
            
        Returns:
            AdvanceDeduction instance
        """
        # Create deduction record
        deduction = AdvanceDeduction.objects.create(
            website=writer_payment.website,
            advance_request=advance_request,
            writer_payment=writer_payment,
            order=getattr(writer_payment, 'order', None),
            amount_deducted=amount
        )
        
        # Update advance request repayment
        advance_request.repaid_amount += amount
        if advance_request.repaid_amount >= advance_request.disbursed_amount:
            advance_request.status = 'repaid'
            advance_request.fully_repaid_at = now()
        advance_request.save()
        
        return deduction
    
    @staticmethod
    def process_advance_deductions(writer_payment):
        """
        Process advance deductions for a writer payment.
        Deducts from outstanding advances until fully repaid.
        
        Args:
            writer_payment: WriterPayment or ScheduledWriterPayment instance
            
        Returns:
            Decimal: Remaining payment amount after deductions
        """
        from writer_management.models import WriterProfile
        from django.db.models import F
        
        # Handle both WriterPayment and ScheduledWriterPayment
        if hasattr(writer_payment, 'writer_wallet'):
            writer_user = writer_payment.writer_wallet.writer
            website = writer_payment.website
        elif hasattr(writer_payment, 'writer'):
            writer_user = writer_payment.writer.user
            website = writer_payment.website
        else:
            logger.warning(f"Unknown payment type: {type(writer_payment)}")
            return getattr(writer_payment, 'amount', Decimal('0.00'))
        
        try:
            writer_profile = WriterProfile.objects.get(
                user=writer_user,
                website=website
            )
        except WriterProfile.DoesNotExist:
            logger.warning(f"WriterProfile not found for payment")
            return getattr(writer_payment, 'amount', Decimal('0.00'))
        
        # Get outstanding advances
        outstanding_advances = WriterAdvancePaymentRequest.objects.filter(
            writer=writer_profile,
            website=website,
            status__in=['approved', 'disbursed']
        ).exclude(
            repaid_amount__gte=F('disbursed_amount')
        ).order_by('requested_at')
        
        remaining_payment = getattr(writer_payment, 'amount', Decimal('0.00'))
        original_amount = remaining_payment
        
        for advance in outstanding_advances:
            if remaining_payment <= 0:
                break
            
            outstanding = advance.outstanding_amount
            if outstanding <= 0:
                continue
            
            # Deduct up to outstanding amount or remaining payment, whichever is less
            deduction_amount = min(outstanding, remaining_payment)
            
            # Create deduction record
            # Try to get order from payment if available
            order = None
            if hasattr(writer_payment, 'order'):
                order = writer_payment.order
            elif hasattr(writer_payment, 'orders'):
                # For scheduled payments with multiple orders
                orders = writer_payment.orders.all()
                order = orders.first() if orders.exists() else None
            
            AdvanceDeduction.objects.create(
                website=website,
                advance_request=advance,
                writer_payment=writer_payment if hasattr(writer_payment, 'writer_wallet') else None,
                order=order,
                amount_deducted=deduction_amount
            )
            
            # Update advance request repayment
            advance.repaid_amount += deduction_amount
            if advance.repaid_amount >= advance.disbursed_amount:
                advance.status = 'repaid'
                advance.fully_repaid_at = now()
            advance.save()
            
            remaining_payment -= deduction_amount
        
        if remaining_payment != original_amount:
            logger.info(
                f"Advance deductions: ${original_amount} -> ${remaining_payment} "
                f"(deducted ${original_amount - remaining_payment})"
            )
        
        return remaining_payment

