"""
Service for managing fine operations - admin interface for issuing fines.
"""

from typing import Optional
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError

from orders.models import Order
from fines.models import Fine, FineTypeConfig
from fines.services.fine_type_service import FineTypeService


class FineManagementService:
    """
    Service for admin fine management operations.
    """
    
    @staticmethod
    def issue_custom_fine(
        order: Order,
        fine_type_code: str,
        reason: str,
        issued_by,
        amount: Optional[Decimal] = None,
        use_config: bool = True
    ) -> Fine:
        """
        Issue a fine with optional custom amount override.
        
        Args:
            order: Order to fine
            fine_type_code: Fine type code (must exist in FineTypeConfig)
            reason: Detailed reason for fine
            issued_by: Admin issuing fine
            amount: Custom amount (overrides config if provided)
            use_config: If True, uses FineTypeConfig; if False, uses amount directly
            
        Returns:
            Fine: Created fine instance
        """
        if use_config:
            # Use FineTypeService (respects config or uses custom amount)
            return FineTypeService.issue_fine(
                order=order,
                fine_type_code=fine_type_code,
                reason=reason,
                issued_by=issued_by,
                custom_amount=amount
            )
        else:
            # Direct fine creation (legacy/bypass config)
            if not amount:
                raise ValidationError("Amount required when use_config=False")
            
            return FineTypeService.issue_fine(
                order=order,
                fine_type_code=fine_type_code,
                reason=reason,
                issued_by=issued_by,
                custom_amount=amount
            )
    
    @staticmethod
    def get_available_fine_types(website=None):
        """
        Get all available fine types for a website.
        
        Args:
            website: Website instance (optional)
            
        Returns:
            QuerySet: FineTypeConfig instances
        """
        queryset = FineTypeConfig.objects.filter(active=True)
        
        if website:
            # Get website-specific and global types
            return queryset.filter(
                models.Q(website=website) | models.Q(website__isnull=True)
            )
        else:
            # Only global types
            return queryset.filter(website__isnull=True)

