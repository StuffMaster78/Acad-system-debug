"""
Service for managing fine types and issuing fines using admin-configured types.
"""

from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from typing import Optional, Tuple

from orders.models import Order
from fines.models import FineTypeConfig, Fine, FineStatus
from fines.services.compensation import adjust_writer_compensation
from audit_logging.services.audit_log_service import AuditLogService


class FineTypeService:
    """
    Service for managing fine types and issuing fines.
    """
    
    @staticmethod
    def get_fine_type_config(code: str, website=None) -> Optional[FineTypeConfig]:
        """
        Get active fine type config by code.
        
        Args:
            code: Fine type code (e.g., 'quality_issue')
            website: Website instance (optional, for website-specific configs)
            
        Returns:
            FineTypeConfig or None
        """
        queryset = FineTypeConfig.objects.filter(code=code, active=True)
        
        if website:
            # Try website-specific first, then global
            config = queryset.filter(website=website).first()
            if config:
                return config
            return queryset.filter(website__isnull=True).first()
        else:
            # Return first active config (prefer website-specific if website provided)
            return queryset.first()
    
    @staticmethod
    def issue_fine(
        order: Order,
        fine_type_code: str,
        reason: str,
        issued_by,
        custom_amount: Optional[Decimal] = None,
        **kwargs
    ) -> Fine:
        """
        Issue a fine using admin-configured fine type.
        
        Args:
            order: Order to fine
            fine_type_code: Fine type code (e.g., 'quality_issue', 'late_submission')
            reason: Reason for the fine
            issued_by: User issuing the fine (admin/system)
            custom_amount: Optional custom amount (overrides config)
            **kwargs: Additional parameters (e.g., hours_late for progressive_hourly)
            
        Returns:
            Fine: Created Fine instance
            
        Raises:
            ValueError: If fine type config not found or invalid
        """
        # Get fine type config
        config = FineTypeService.get_fine_type_config(fine_type_code, order.website)
        
        if not config:
            raise ValueError(
                f"No active fine type config found for code '{fine_type_code}'. "
                "Admin must create a FineTypeConfig first."
            )
        
        # Calculate fine amount
        if custom_amount:
            fine_amount = custom_amount
        else:
            hours_late = kwargs.get('hours_late')
            base_amount = kwargs.get('base_amount')
            fine_amount = config.calculate_fine_amount(
                order=order,
                hours_late=hours_late,
                base_amount=base_amount
            )
        
        if fine_amount <= 0:
            raise ValueError(f"Fine amount must be positive (calculated: {fine_amount})")
        
        # Create fine
        fine = Fine.objects.create(
            order=order,
            fine_type=fine_type_code,  # Legacy field for backward compatibility
            fine_type_config=config,  # New field
            amount=fine_amount,
            reason=reason,
            issued_by=issued_by,
            status=FineStatus.ISSUED,
            imposed_at=timezone.now()
        )
        
        # Adjust writer compensation
        adjust_writer_compensation(order, -fine_amount)
        
        # Audit log
        AuditLogService.log_auto(
            actor=issued_by or order.assigned_writer,
            action="fine_issued",
            target=fine,
            changes={
                "fine_type": fine_type_code,
                "amount": str(fine_amount),
                "reason": reason
            },
            context={
                "order_id": order.id,
                "fine_type_config_id": config.id
            }
        )
        
        return fine
    
    @staticmethod
    def create_fine_type(
        code: str,
        name: str,
        created_by,
        website=None,
        calculation_type='fixed',
        fixed_amount=None,
        percentage=None,
        base_amount='writer_compensation',
        min_amount=None,
        max_amount=None,
        description='',
        is_system_defined='admin'
    ) -> FineTypeConfig:
        """
        Create a new fine type configuration.
        
        Args:
            code: Unique code (e.g., 'quality_issue')
            name: Display name (e.g., 'Quality Issue')
            created_by: Admin user creating this
            website: Website (None = all websites)
            calculation_type: 'fixed', 'percentage', or 'progressive_hourly'
            fixed_amount: Fixed amount (if calculation_type='fixed')
            percentage: Percentage (if calculation_type='percentage')
            base_amount: 'writer_compensation' or 'total_price'
            min_amount: Minimum fine amount
            max_amount: Maximum fine amount
            description: Description of when this fine applies
            is_system_defined: 'system' or 'admin'
            
        Returns:
            FineTypeConfig: Created config
            
        Raises:
            ValidationError: If configuration is invalid
        """
        config = FineTypeConfig(
            code=code,
            name=name,
            created_by=created_by,
            website=website,
            calculation_type=calculation_type,
            fixed_amount=fixed_amount,
            percentage=percentage,
            base_amount=base_amount,
            min_amount=min_amount,
            max_amount=max_amount,
            description=description,
            is_system_defined=is_system_defined,
            active=True
        )
        
        config.full_clean()
        config.save()
        
        return config

