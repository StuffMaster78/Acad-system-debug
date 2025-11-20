"""
Service for admin to manually create and configure class bundles with custom pricing,
deposits, and installments.
"""

import logging
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from class_management.models import ClassBundle, ClassInstallment
from websites.models import Website
from discounts.models.discount import Discount
from notifications_system.services.notification_helper import NotificationHelper

logger = logging.getLogger(__name__)


class ClassBundleAdminService:
    """
    Service for admin to manage class bundles with manual configuration.
    """
    
    @staticmethod
    @transaction.atomic
    def create_manual_bundle(
        client,
        website: Website,
        admin_user,
        total_price: Decimal,
        number_of_classes: int,
        deposit_required: Decimal = None,
        installments_enabled: bool = False,
        installment_count: int = None,
        duration: str = None,
        level: str = None,
        bundle_size: int = None,
        start_date=None,
        end_date=None,
        discount_code: str = None,
        discount_id: int = None,
        **kwargs
    ) -> ClassBundle:
        """
        Create a class bundle with manual pricing set by admin.
        
        Args:
            client: Client user
            website: Website context
            admin_user: Admin creating the bundle
            total_price: Original agreed price (before discount if discount applied)
            number_of_classes: Number of classes client needs
            deposit_required: Deposit amount required (defaults to 0 or percentage)
            installments_enabled: Whether to enable installments
            installment_count: Number of installments (if enabled)
            duration: Optional duration code
            level: Optional level (undergrad/grad)
            bundle_size: Optional bundle size
            start_date: Optional start date (date A)
            end_date: Optional end date (date B)
            discount_code: Optional discount code to apply
            discount_id: Optional discount ID to apply
            **kwargs: Additional fields for ClassBundle
        
        Returns:
            ClassBundle: Created bundle
        """
        # Apply discount if provided
        discount = None
        original_price = total_price
        final_price = total_price
        
        if discount_code:
            discount = Discount.objects.filter(
                discount_code=discount_code,
                website=website,
                is_active=True
            ).first()
            if not discount:
                raise ValidationError(f"Discount code '{discount_code}' not found or inactive.")
        elif discount_id:
            discount = Discount.objects.filter(
                id=discount_id,
                website=website,
                is_active=True
            ).first()
            if not discount:
                raise ValidationError(f"Discount ID '{discount_id}' not found or inactive.")
        
        # Calculate discounted price if discount provided
        if discount:
            # Apply discount calculation to original price
            if discount.discount_type == 'percentage':
                discount_amount = (discount.value / 100) * total_price
            else:  # fixed
                discount_amount = discount.value
            
            original_price = total_price  # Store original
            final_price = max(Decimal('0'), total_price - discount_amount)  # Apply discount
            
            logger.info(
                f"Applied discount {discount.discount_code} to bundle: "
                f"${original_price} -> ${final_price} (${discount_amount} off)"
            )
        
        # Use final_price (after discount) for all calculations
        total_price = final_price
        
        # Validate deposit
        if deposit_required is None:
            deposit_required = Decimal('0')
        
        if deposit_required < 0:
            raise ValidationError("Deposit cannot be negative.")
        
        if deposit_required > total_price:
            raise ValidationError("Deposit cannot exceed total price.")
        
        # Validate installments
        if installments_enabled:
            if not installment_count or installment_count < 1:
                raise ValidationError("Installment count must be at least 1 if installments are enabled.")
            
            remaining_after_deposit = total_price - deposit_required
            if remaining_after_deposit <= 0:
                raise ValidationError("Cannot enable installments when deposit equals or exceeds total price.")
        
        # Create bundle
        bundle = ClassBundle.objects.create(
            client=client,
            website=website,
            pricing_source='manual',
            total_price=total_price,
            original_price=original_price if discount else None,
            discount=discount,
            number_of_classes=number_of_classes,
            deposit_required=deposit_required,
            deposit_paid=Decimal('0'),
            balance_remaining=total_price - deposit_required,
            installments_enabled=installments_enabled,
            installment_count=installment_count if installments_enabled else None,
            duration=duration,
            level=level,
            bundle_size=bundle_size,
            start_date=start_date,
            end_date=end_date,
            created_by_admin=admin_user,
            **kwargs
        )
        
        # Track discount usage if discount was applied
        if discount:
            from discounts.services.discount_usage_tracker import DiscountUsageTracker
            
            # Calculate discount amount for tracking
            if discount.discount_type == 'percentage':
                tracked_amount = (discount.value / 100) * original_price
            else:
                tracked_amount = discount.value
            
            DiscountUsageTracker.track_usage(
                discount=discount,
                user=client,
                amount=tracked_amount,
                related_object=bundle
            )
        
        logger.info(
            f"Admin {admin_user.id} created manual bundle {bundle.id} for client {client.id} "
            f"(total: ${total_price}, deposit: ${deposit_required})"
        )
        
        # Generate installments if enabled
        if installments_enabled:
            ClassBundleAdminService._generate_installments(
                bundle=bundle,
                count=installment_count,
                interval_weeks=2  # Default 2 weeks between installments
            )
        
        # Send notification to client
        try:
            # Get client profile
            from client_management.models import ClientProfile
            client_profile = ClientProfile.objects.filter(user=client, website=website).first()
            if client_profile:
                NotificationHelper.notify_class_bundle_created(
                    class_bundle=bundle,
                    client_profile=client_profile
                )
        except Exception as e:
            logger.error(f"Failed to send class bundle created notification: {e}")
        
        return bundle
    
    @staticmethod
    @transaction.atomic
    def update_bundle_pricing(
        bundle: ClassBundle,
        admin_user,
        total_price: Decimal = None,
        deposit_required: Decimal = None,
        **kwargs
    ) -> ClassBundle:
        """
        Update pricing for an existing bundle (admin only).
        
        Args:
            bundle: ClassBundle to update
            admin_user: Admin making the change
            total_price: New total price
            deposit_required: New deposit required
            **kwargs: Other fields to update
        
        Returns:
            ClassBundle: Updated bundle
        """
        # Can only update if no payments have been made
        if bundle.deposit_paid > 0 or bundle.installments.filter(is_paid=True).exists():
            raise ValidationError("Cannot update pricing after payments have been made.")
        
        if total_price is not None:
            if total_price < 0:
                raise ValidationError("Total price cannot be negative.")
            bundle.total_price = total_price
        
        if deposit_required is not None:
            if deposit_required < 0:
                raise ValidationError("Deposit cannot be negative.")
            if deposit_required > bundle.total_price:
                raise ValidationError("Deposit cannot exceed total price.")
            bundle.deposit_required = deposit_required
        
        # Update other fields
        for key, value in kwargs.items():
            if hasattr(bundle, key):
                setattr(bundle, key, value)
        
        # Recalculate balance
        bundle.balance_remaining = bundle.total_price - bundle.deposit_required
        bundle.save()
        
        logger.info(
            f"Admin {admin_user.id} updated pricing for bundle {bundle.id} "
            f"(total: ${bundle.total_price}, deposit: ${bundle.deposit_required})"
        )
        
        return bundle
    
    @staticmethod
    @transaction.atomic
    def configure_installments(
        bundle: ClassBundle,
        admin_user,
        installment_count: int,
        interval_weeks: int = 2,
        amounts: list = None
    ) -> ClassBundle:
        """
        Configure or update installments for a bundle.
        
        Args:
            bundle: ClassBundle to configure
            admin_user: Admin configuring
            installment_count: Number of installments
            interval_weeks: Weeks between installments
            amounts: Optional list of specific amounts per installment (must sum to balance)
        
        Returns:
            ClassBundle: Updated bundle
        """
        # Check if any installments are already paid
        if bundle.installments.filter(is_paid=True).exists():
            raise ValidationError("Cannot reconfigure installments after payments have been made.")
        
        # Clear existing unpaid installments
        bundle.installments.filter(is_paid=False).delete()
        
        # Calculate amounts
        balance_after_deposit = bundle.total_price - bundle.deposit_required
        
        if amounts:
            # Use custom amounts
            if len(amounts) != installment_count:
                raise ValidationError(f"Must provide exactly {installment_count} installment amounts.")
            if sum(Decimal(str(a)) for a in amounts) != balance_after_deposit:
                raise ValidationError("Installment amounts must sum to balance after deposit.")
            installment_amounts = [Decimal(str(a)) for a in amounts]
        else:
            # Equal installments
            per_installment = balance_after_deposit / installment_count
            # Handle rounding: last installment gets remainder
            installment_amounts = [per_installment] * (installment_count - 1)
            installment_amounts.append(balance_after_deposit - sum(installment_amounts))
        
        # Generate installments
        ClassBundleAdminService._generate_installments(
            bundle=bundle,
            count=installment_count,
            interval_weeks=interval_weeks,
            amounts=installment_amounts
        )
        
        bundle.installments_enabled = True
        bundle.installment_count = installment_count
        bundle.save()
        
        logger.info(
            f"Admin {admin_user.id} configured {installment_count} installments for bundle {bundle.id}"
        )
        
        return bundle
    
    @staticmethod
    def _generate_installments(
        bundle: ClassBundle,
        count: int,
        interval_weeks: int = 2,
        amounts: list = None
    ):
        """
        Generate installment records for a bundle.
        
        Args:
            bundle: ClassBundle
            count: Number of installments
            interval_weeks: Weeks between installments
            amounts: Optional list of amounts (must match count)
        """
        base_date = timezone.now().date()
        
        if amounts is None:
            balance = bundle.total_price - bundle.deposit_required
            per_installment = balance / count
            amounts = [per_installment] * (count - 1)
            amounts.append(balance - sum(amounts))
        
        installments = []
        for i, amount in enumerate(amounts):
            due_date = base_date + timedelta(weeks=(i + 1) * interval_weeks)
            
            installments.append(
                ClassInstallment(
                    class_bundle=bundle,
                    amount=amount,
                    due_date=due_date,
                    installment_number=i + 1,
                    is_paid=False
                )
            )
        
        ClassInstallment.objects.bulk_create(installments)
    
    @staticmethod
    @transaction.atomic
    def disable_installments(bundle: ClassBundle, admin_user) -> ClassBundle:
        """
        Disable installments for a bundle (only if none are paid).
        
        Args:
            bundle: ClassBundle
            admin_user: Admin performing action
        
        Returns:
            ClassBundle: Updated bundle
        """
        if bundle.installments.filter(is_paid=True).exists():
            raise ValidationError("Cannot disable installments after payments have been made.")
        
        bundle.installments.all().delete()
        bundle.installments_enabled = False
        bundle.installment_count = None
        bundle.save()
        
        logger.info(f"Admin {admin_user.id} disabled installments for bundle {bundle.id}")
        
        return bundle

