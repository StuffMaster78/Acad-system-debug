"""
Loyalty Points Redemption Service
Handles redemption validation, processing, and fulfillment.
"""
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid

from loyalty_management.models import (
    RedemptionRequest,
    RedemptionItem,
    LoyaltyTransaction
)
from discounts.models.discount import Discount
from wallet.models import Wallet, WalletTransaction


class RedemptionService:
    """
    Service for handling loyalty points redemption operations.
    """
    
    @staticmethod
    @transaction.atomic
    def create_redemption_request(client_profile, item_id, fulfillment_details=None):
        """
        Create a redemption request and deduct points.
        
        Args:
            client_profile: ClientProfile instance
            item_id: ID of RedemptionItem to redeem
            fulfillment_details: Optional dict with fulfillment info
        
        Returns:
            RedemptionRequest instance
        
        Raises:
            ValidationError: If redemption is not valid
        """
        try:
            item = RedemptionItem.objects.get(id=item_id, website=client_profile.website)
        except RedemptionItem.DoesNotExist:
            raise ValidationError("Redemption item not found")
        
        # Validate redemption
        can_redeem, message = item.can_redeem(client_profile)
        if not can_redeem:
            raise ValidationError(message)
        
        # Check stock
        if item.stock_quantity is not None:
            if item.stock_quantity <= 0:
                raise ValidationError("Item out of stock")
            # Reserve stock (will be decremented on approval)
        
        # Create redemption request
        redemption = RedemptionRequest.objects.create(
            website=client_profile.website,
            client=client_profile,
            item=item,
            points_used=item.points_required,
            status='pending',
            fulfillment_details=fulfillment_details or {}
        )
        
        # For automatic items (discounts, cash), auto-approve
        if item.redemption_type in ['discount', 'cash']:
            RedemptionService.approve_redemption(redemption, client_profile.website)
        
        return redemption
    
    @staticmethod
    @transaction.atomic
    def approve_redemption(redemption, approved_by):
        """
        Approve a redemption request and fulfill it.
        
        Args:
            redemption: RedemptionRequest instance
            approved_by: User who approved (admin/superadmin)
        """
        if redemption.status != 'pending':
            raise ValidationError(f"Cannot approve redemption with status: {redemption.status}")
        
        # Deduct points
        if redemption.client.loyalty_points < redemption.points_used:
            raise ValidationError("Client has insufficient points")
        
        redemption.client.loyalty_points -= redemption.points_used
        redemption.client.save()
        
        # Create loyalty transaction
        LoyaltyTransaction.objects.create(
            website=redemption.website,
            client=redemption.client,
            points=-redemption.points_used,  # Negative for redemption
            transaction_type='redeem',
            reason=f"Redemption: {redemption.item.name}",
            redemption_request=redemption
        )
        
        # Update redemption status
        redemption.status = 'approved'
        redemption.approved_by = approved_by
        redemption.approved_at = timezone.now()
        
        # Fulfill based on type
        RedemptionService._fulfill_redemption(redemption)
        
        redemption.save()
        
        # Update item stats
        redemption.item.total_redemptions += 1
        if redemption.item.stock_quantity is not None:
            redemption.item.stock_quantity -= 1
        redemption.item.save()
        
        # Send notification
        try:
            from notifications_system.services.notification_helper import NotificationHelper
            NotificationHelper.notify_redemption_approved(
                redemption_request=redemption,
                fulfillment_code=redemption.fulfillment_code
            )
        except Exception:
            # Notification failures shouldn't break redemption flow
            pass
    
    @staticmethod
    def _fulfill_redemption(redemption):
        """
        Fulfill a redemption based on its type.
        """
        item = redemption.item
        
        if item.redemption_type == 'cash':
            # Add to wallet
            wallet, _ = Wallet.objects.get_or_create(
                user=redemption.client.user,
                website=redemption.website,
                defaults={'balance': Decimal('0.00')}
            )
            amount = item.discount_amount or Decimal('0.00')
            wallet.balance += amount
            wallet.save()
            
            # Create wallet transaction
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='credit',
                amount=amount,
                description=f"Loyalty points redemption: {item.name}",
                website=redemption.website
            )
            
            redemption.fulfillment_code = f"WALLET-{wallet.id}-{int(timezone.now().timestamp())}"
        
        elif item.redemption_type == 'discount':
            # Generate discount code
            discount_code = f"LOYALTY-{uuid.uuid4().hex[:8].upper()}"
            
            # Create discount
            discount = Discount.objects.create(
                website=redemption.website,
                discount_code=discount_code,
                discount_type='fixed' if item.discount_amount else 'percentage',
                value=item.discount_amount or item.discount_percentage or Decimal('10.00'),
                min_order_value=Decimal('0.00'),
                max_uses=1,
                max_uses_per_user=1,
                is_active=True,
                valid_from=timezone.now(),
                valid_until=timezone.now() + timezone.timedelta(days=90)
            )
            
            redemption.fulfillment_code = discount_code
            redemption.fulfillment_details = {
                'discount_id': discount.id,
                'discount_type': discount.discount_type,
                'value': str(discount.value)
            }
        
        elif item.redemption_type == 'voucher':
            # Generate voucher code
            voucher_code = f"VOUCHER-{uuid.uuid4().hex[:12].upper()}"
            redemption.fulfillment_code = voucher_code
        
        redemption.status = 'fulfilled'
        redemption.fulfilled_by = redemption.approved_by
        redemption.fulfilled_at = timezone.now()
    
    @staticmethod
    def reject_redemption(redemption, rejected_by, reason):
        """
        Reject a redemption request.
        
        Args:
            redemption: RedemptionRequest instance
            rejected_by: User who rejected
            reason: Reason for rejection
        """
        if redemption.status != 'pending':
            raise ValidationError(f"Cannot reject redemption with status: {redemption.status}")
        
        redemption.status = 'rejected'
        redemption.rejected_by = rejected_by
        redemption.rejection_reason = reason
        redemption.rejected_at = timezone.now()
        redemption.save()
        
        # Send notification
        try:
            from notifications_system.services.notification_helper import NotificationHelper
            NotificationHelper.notify_redemption_rejected(
                redemption_request=redemption,
                reason=reason
            )
        except Exception:
            # Notification failures shouldn't break rejection flow
            pass
    
    @staticmethod
    def cancel_redemption(redemption, cancelled_by):
        """
        Cancel a redemption request (by client or admin).
        """
        if redemption.status not in ['pending', 'approved']:
            raise ValidationError(f"Cannot cancel redemption with status: {redemption.status}")
        
        # If approved but not fulfilled, refund points
        if redemption.status == 'approved' and redemption.status != 'fulfilled':
            redemption.client.loyalty_points += redemption.points_used
            redemption.client.save()
            
            # Create refund transaction
            LoyaltyTransaction.objects.create(
                website=redemption.website,
                client=redemption.client,
                points=redemption.points_used,
                transaction_type='add',
                reason=f"Cancelled redemption: {redemption.item.name}",
                redemption_request=redemption
            )
        
        redemption.status = 'cancelled'
        redemption.save()
    
    @staticmethod
    def get_client_redemptions(client_profile, status=None):
        """
        Get redemption history for a client.
        
        Args:
            client_profile: ClientProfile instance
            status: Optional status filter
        
        Returns:
            QuerySet of RedemptionRequest
        """
        queryset = RedemptionRequest.objects.filter(
            client=client_profile
        ).select_related('item', 'item__category').order_by('-requested_at')
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset

