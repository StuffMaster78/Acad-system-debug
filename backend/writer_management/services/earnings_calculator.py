"""
Service to calculate writer earnings based on level configuration and order details.
Supports multiple earning modes: fixed per page, percentage of cost, percentage of total.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class WriterEarningsCalculator:
    """
    Calculates writer earnings based on level configuration and order details.
    """
    
    @staticmethod
    def calculate_earnings(
        writer_level,
        order,
        is_urgent: bool = False,
        is_technical: bool = False
    ) -> Decimal:
        """
        Calculate writer earnings based on level's earning mode.
        
        Args:
            writer_level: WriterLevel instance
            order: Order instance with number_of_pages, number_of_slides, total_price, discounted_amount
            is_urgent: Whether the order is urgent
            is_technical: Whether the order is technical
            
        Returns:
            Decimal: Calculated earnings amount
        """
        if writer_level.earning_mode == 'fixed_per_page':
            return WriterEarningsCalculator._calculate_fixed_earnings(
                writer_level, order, is_urgent, is_technical
            )
        elif writer_level.earning_mode == 'percentage_of_order_cost':
            return WriterEarningsCalculator._calculate_percentage_of_cost(
                writer_level, order, is_urgent, is_technical
            )
        elif writer_level.earning_mode == 'percentage_of_order_total':
            return WriterEarningsCalculator._calculate_percentage_of_total(
                writer_level, order, is_urgent, is_technical
            )
        else:
            # Fallback to fixed if mode is invalid
            logger.warning(f"Invalid earning_mode '{writer_level.earning_mode}' for level {writer_level.name}, using fixed_per_page")
            return WriterEarningsCalculator._calculate_fixed_earnings(
                writer_level, order, is_urgent, is_technical
            )
    
    @staticmethod
    def _calculate_fixed_earnings(writer_level, order, is_urgent, is_technical):
        """Fixed per page/slide calculation (existing logic enhanced)"""
        pages = getattr(order, 'number_of_pages', 0) or 0
        slides = getattr(order, 'number_of_slides', 0) or 0
        
        base = (
            Decimal(str(pages)) * writer_level.base_pay_per_page +
            Decimal(str(slides)) * writer_level.base_pay_per_slide
        )
        
        # Urgency adjustments
        if is_urgent:
            # Percentage increase
            urgency_multiplier = Decimal('1') + (writer_level.urgency_percentage_increase / Decimal('100'))
            base = base * urgency_multiplier
            # Additional per page
            base += Decimal(str(pages)) * writer_level.urgency_additional_per_page
        
        # Technical adjustments
        if is_technical:
            base += (
                Decimal(str(pages)) * writer_level.technical_order_adjustment_per_page +
                Decimal(str(slides)) * writer_level.technical_order_adjustment_per_slide
            )
        
        return base.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def _calculate_percentage_of_cost(writer_level, order, is_urgent, is_technical):
        """Percentage of order cost (before discounts)"""
        pages = getattr(order, 'number_of_pages', 0) or 0
        slides = getattr(order, 'number_of_slides', 0) or 0
        order_cost = Decimal(str(getattr(order, 'total_price', 0) or 0))
        
        # Calculate base earnings as percentage of cost
        if writer_level.earnings_percentage_of_cost > 0:
            base_earnings = order_cost * (writer_level.earnings_percentage_of_cost / Decimal('100'))
        else:
            # Fallback to fixed if percentage not set
            base_earnings = (
                Decimal(str(pages)) * writer_level.base_pay_per_page +
                Decimal(str(slides)) * writer_level.base_pay_per_slide
            )
        
        # Ensure minimum (fallback to fixed rates if percentage is too low)
        min_earnings = (
            Decimal(str(pages)) * writer_level.base_pay_per_page +
            Decimal(str(slides)) * writer_level.base_pay_per_slide
        )
        base_earnings = max(base_earnings, min_earnings)
        
        # Apply urgency multiplier
        if is_urgent:
            urgency_multiplier = Decimal('1') + (writer_level.urgency_percentage_increase / Decimal('100'))
            base_earnings = base_earnings * urgency_multiplier
            base_earnings += Decimal(str(pages)) * writer_level.urgency_additional_per_page
        
        # Technical bonus
        if is_technical:
            base_earnings += (
                Decimal(str(pages)) * writer_level.technical_order_adjustment_per_page +
                Decimal(str(slides)) * writer_level.technical_order_adjustment_per_slide
            )
        
        return base_earnings.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def _calculate_percentage_of_total(writer_level, order, is_urgent, is_technical):
        """Percentage of order total (after discounts)"""
        pages = getattr(order, 'number_of_pages', 0) or 0
        slides = getattr(order, 'number_of_slides', 0) or 0
        
        # Get discounted amount (after discounts) or fallback to total_price
        discounted_total = Decimal(str(
            getattr(order, 'discounted_amount', None) or 
            getattr(order, 'total_price', 0) or 0
        ))
        
        # Calculate base earnings as percentage of total
        if writer_level.earnings_percentage_of_total > 0:
            base_earnings = discounted_total * (writer_level.earnings_percentage_of_total / Decimal('100'))
        else:
            # Fallback to fixed if percentage not set
            base_earnings = (
                Decimal(str(pages)) * writer_level.base_pay_per_page +
                Decimal(str(slides)) * writer_level.base_pay_per_slide
            )
        
        # Ensure minimum (fallback to fixed rates if percentage is too low)
        min_earnings = (
            Decimal(str(pages)) * writer_level.base_pay_per_page +
            Decimal(str(slides)) * writer_level.base_pay_per_slide
        )
        base_earnings = max(base_earnings, min_earnings)
        
        # Apply urgency multiplier
        if is_urgent:
            urgency_multiplier = Decimal('1') + (writer_level.urgency_percentage_increase / Decimal('100'))
            base_earnings = base_earnings * urgency_multiplier
            base_earnings += Decimal(str(pages)) * writer_level.urgency_additional_per_page
        
        # Technical bonus
        if is_technical:
            base_earnings += (
                Decimal(str(pages)) * writer_level.technical_order_adjustment_per_page +
                Decimal(str(slides)) * writer_level.technical_order_adjustment_per_slide
            )
        
        return base_earnings.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calculate_estimated_earnings(
        writer_level,
        pages: int = 0,
        slides: int = 0,
        order_total: Optional[Decimal] = None,
        order_cost: Optional[Decimal] = None,
        is_urgent: bool = False,
        is_technical: bool = False
    ) -> dict:
        """
        Calculate estimated earnings for display purposes.
        Returns a breakdown of the calculation.
        
        Args:
            writer_level: WriterLevel instance
            pages: Number of pages
            slides: Number of slides
            order_total: Order total (after discounts) - for percentage_of_order_total mode
            order_cost: Order cost (before discounts) - for percentage_of_order_cost mode
            is_urgent: Whether order is urgent
            is_technical: Whether order is technical
            
        Returns:
            dict with earnings breakdown
        """
        # Create a mock order object
        class MockOrder:
            def __init__(self, pages, slides, total_price, discounted_amount=None):
                self.number_of_pages = pages
                self.number_of_slides = slides
                self.total_price = total_price
                self.discounted_amount = discounted_amount or total_price
        
        if order_total:
            mock_order = MockOrder(pages, slides, order_cost or order_total, order_total)
        elif order_cost:
            mock_order = MockOrder(pages, slides, order_cost, order_cost)
        else:
            # Estimate order cost based on pages (rough estimate)
            estimated_cost = Decimal(str(pages)) * Decimal('10')  # $10/page estimate
            mock_order = MockOrder(pages, slides, estimated_cost, estimated_cost)
        
        total_earnings = WriterEarningsCalculator.calculate_earnings(
            writer_level, mock_order, is_urgent, is_technical
        )
        
        # Calculate breakdown
        breakdown = {
            'total_earnings': float(total_earnings),
            'earning_mode': writer_level.earning_mode,
            'base_earnings': 0.0,
            'urgency_bonus': 0.0,
            'technical_bonus': 0.0,
        }
        
        # Calculate base
        if writer_level.earning_mode == 'fixed_per_page':
            breakdown['base_earnings'] = float(
                Decimal(str(pages)) * writer_level.base_pay_per_page +
                Decimal(str(slides)) * writer_level.base_pay_per_slide
            )
        elif writer_level.earning_mode == 'percentage_of_order_cost':
            order_value = order_cost or Decimal(str(pages)) * Decimal('10')
            breakdown['base_earnings'] = float(
                order_value * (writer_level.earnings_percentage_of_cost / Decimal('100'))
            )
        elif writer_level.earning_mode == 'percentage_of_order_total':
            order_value = order_total or order_cost or Decimal(str(pages)) * Decimal('10')
            breakdown['base_earnings'] = float(
                order_value * (writer_level.earnings_percentage_of_total / Decimal('100'))
            )
        
        # Calculate urgency bonus
        if is_urgent:
            urgency_multiplier = writer_level.urgency_percentage_increase / Decimal('100')
            breakdown['urgency_bonus'] = float(breakdown['base_earnings'] * urgency_multiplier)
            breakdown['urgency_bonus'] += float(Decimal(str(pages)) * writer_level.urgency_additional_per_page)
        
        # Calculate technical bonus
        if is_technical:
            breakdown['technical_bonus'] = float(
                Decimal(str(pages)) * writer_level.technical_order_adjustment_per_page +
                Decimal(str(slides)) * writer_level.technical_order_adjustment_per_slide
            )
        
        return breakdown

