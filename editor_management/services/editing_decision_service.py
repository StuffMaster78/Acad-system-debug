"""
Service to determine if an order should undergo editing based on configuration and order attributes.
"""

from django.utils.timezone import now
from datetime import timedelta
from typing import Tuple, Optional

from orders.models import Order
from orders.order_enums import OrderStatus, OrderFlags
from order_configs.models import EditingRequirementConfig


class EditingDecisionService:
    """
    Determines if an order should go through editing based on:
    - Admin-set requires_editing flag
    - Urgency status
    - Submission timing (before deadline)
    - Configuration settings
    """
    
    URGENT_THRESHOLD_HOURS = 24  # Orders with < 24 hours to deadline are urgent
    
    @staticmethod
    def should_undergo_editing(order: Order, website=None) -> Tuple[bool, Optional[str]]:
        """
        Determine if an order should undergo editing.
        
        Args:
            order: The order to check
            website: Optional website (will use order.website if not provided)
            
        Returns:
            Tuple[bool, Optional[str]]: 
                - (True, None) if should go to editing
                - (False, reason) if should skip editing (reason explains why)
        """
        website = website or order.website
        
        # 1. Check admin-set flag first (takes highest priority)
        if order.requires_editing is True:
            return (True, None)  # Admin explicitly requires editing
        
        if order.requires_editing is False:
            return (False, "Admin disabled editing for this order")
        
        # 2. Check if order is urgent (skip editing)
        if EditingDecisionService._is_urgent(order):
            return (False, "Order is urgent - skipping editing")
        
        # 3. Get editing configuration
        config = EditingRequirementConfig.objects.filter(website=website).first()
        
        if not config:
            # No config - use defaults (enable editing)
            return (True, None)
        
        # 4. Check if editing is disabled globally
        if not config.enable_editing_by_default:
            # Even if disabled globally, check for specific requirements
            if EditingDecisionService._has_special_requirements(order, config):
                return (True, "Special requirement (first order or high value)")
            return (False, "Editing disabled by default in configuration")
        
        # 5. Check if order was submitted early (before deadline)
        if config.allow_editing_for_early_submissions:
            if EditingDecisionService._is_early_submission(order, config):
                return (True, "Order submitted early - eligible for editing")
        
        # 6. Check special requirements (first order, high value)
        if EditingDecisionService._has_special_requirements(order, config):
            return (True, "Special requirement (first order or high value)")
        
        # 7. Default: use enable_editing_by_default
        if config.enable_editing_by_default:
            return (True, None)
        
        return (False, "Editing not required based on configuration")
    
    @staticmethod
    def _is_urgent(order: Order) -> bool:
        """
        Check if order is urgent.
        
        Urgent if:
        - is_urgent flag is True
        - URGENT_ORDER flag is set
        - Deadline is less than URGENT_THRESHOLD_HOURS away
        """
        if order.is_urgent:
            return True
        
        if order.flags and OrderFlags.URGENT_ORDER.value in order.flags:
            return True
        
        if order.client_deadline:
            time_until_deadline = order.client_deadline - now()
            if time_until_deadline < timedelta(hours=EditingDecisionService.URGENT_THRESHOLD_HOURS):
                return True
        
        return False
    
    @staticmethod
    def _is_early_submission(order: Order, config: EditingRequirementConfig) -> bool:
        """
        Check if order was submitted early (before deadline threshold).
        
        Early submission = submitted at least X hours before deadline
        """
        if not order.client_deadline:
            return False
        
        # Check if order status is submitted or under_editing (meaning it was already submitted)
        if order.status not in [OrderStatus.SUBMITTED.value, OrderStatus.UNDER_EDITING.value]:
            # If not yet submitted, check if current time is early relative to deadline
            time_until_deadline = order.client_deadline - now()
            return time_until_deadline >= timedelta(hours=config.early_submission_hours_threshold)
        
        # For already submitted orders, we'd need submission timestamp
        # For now, just check if there's time remaining before deadline
        time_until_deadline = order.client_deadline - now()
        return time_until_deadline >= timedelta(hours=config.early_submission_hours_threshold)
    
    @staticmethod
    def _has_special_requirements(order: Order, config: EditingRequirementConfig) -> bool:
        """
        Check if order has special requirements that mandate editing.
        
        Special requirements:
        - First client order (if enabled)
        - High value order (if enabled)
        """
        # Check first order requirement
        if config.editing_required_for_first_orders:
            if order.flags and OrderFlags.FIRST_CLIENT_ORDER.value in order.flags:
                return True
        
        # Check high value requirement
        if config.editing_required_for_high_value:
            if order.total_price and order.total_price >= config.high_value_threshold:
                return True
            if order.flags and OrderFlags.HIGH_VALUE_ORDER.value in order.flags:
                return True
        
        return False
    
    @staticmethod
    def get_config(website) -> Optional[EditingRequirementConfig]:
        """
        Get editing requirement configuration for a website.
        
        Args:
            website: Website instance
            
        Returns:
            EditingRequirementConfig or None
        """
        return EditingRequirementConfig.objects.filter(website=website).first()

