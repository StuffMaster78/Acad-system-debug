import uuid
from django.db import transaction
from django.utils.timezone import now
from decimal import Decimal
from wallet.models import Wallet, WalletTransaction
from django.apps import apps
from referrals.models import Referral, ReferralCode, ReferralBonusConfig
from loyalty_management.models import LoyaltyTransaction
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from orders.models import Order
class ReferralService:
    """
    Service class to handle referral logic including awarding bonuses, applying discounts,
    and managing referral states. This class encapsulates the logic for managing referrals,
    including checking if a bonus can be awarded, applying discounts to orders, and managing
    the referral state.
    """
    
    def __init__(self, referral: Referral):
        self.referral = referral
        self.config = ReferralBonusConfig.objects.filter(website=referral.website).first()

    def get_orders_for_referral(self, referral_code):
        
        Order = apps.get_model('orders', 'Order')
        return Order.objects.filter(referral_code=referral_code)

    def can_award_bonus(self) -> bool:
        if self.referral.bonus_awarded or not self.config:
            return False

        first_order = self._get_qualifying_order()
        return bool(first_order)

    def _get_qualifying_order(self):
        # Order model uses 'client' field and 'is_paid' boolean field
        return self.referral.referee.orders_as_client.filter(status='completed', is_paid=True).first()
    
    def get_referral_link(self):
        """Dynamically generates a referral link."""
        return f"https://{self.referral.website.domain}/order?ref={self.referral.referral_code}"

    @staticmethod
    def generate_unique_code(user, website):
        """Generates a unique referral code."""
        return f"REF-{user.id}-{uuid.uuid4().hex[:6].upper()}"

    @transaction.atomic
    def award_bonus(self):
        if not self.can_award_bonus():
            return

        wallet = Wallet.objects.select_for_update().get(user=self.referral.referrer)
        bonus_amount = self.config.first_order_bonus

        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='bonus',
            amount=bonus_amount,
            description="Referral Bonus",
            website=self.referral.website,
        )

        LoyaltyTransaction.objects.create(
            client=self.referral.referrer.client_profile,
            points=bonus_amount * 10,
            transaction_type='add',
            reason="Referral Bonus Earned",
        )

        self.referral.bonus_awarded = True
        self.referral.save()

    def apply_discount(self, order: "Order") -> Decimal:
        """
        Applies a referral discount to the order if applicable.
        This method checks if the referral discount can be applied based on
        the order and referral status.
        If the discount is applicable, it updates the order total and
        creates a wallet transaction for the
        referrer.
        """
        if not self.config or self.referral.first_order_bonus_credited:
            return Decimal('0.00')

        # Order model uses 'client' field
        order_client = getattr(order, 'client', None) or getattr(order, 'user', None)
        if not order_client or order_client != self.referral.referee:
            return Decimal('0.00')

        previous_orders = order_client.orders_as_client.exclude(id=order.id).filter(status='completed')
        if previous_orders.exists():
            return Decimal('0.00')

        if self.config.first_order_discount_type == 'percentage':
            discount = (self.config.first_order_discount_amount / Decimal('100')) * order.total
        else:
            discount = min(self.config.first_order_discount_amount, order.total)

        order.total -= discount
        order.save()

        wallet, _ = Wallet.objects.get_or_create(user=self.referral.referrer)
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='referral_bonus',
            amount=discount,
            description=f"Referral Discount Applied for {order_client.username}",
            website=self.referral.website,
        )

        self.referral.first_order_bonus_credited = True
        self.referral.save()

        return discount
    
    def get_referral_bonus(self) -> Decimal:
        """
        Returns the referral bonus amount if applicable.
        This method checks if the referral bonus can be awarded based on the referral status
        and the referral configuration. If the bonus has already been awarded or if the
        referral configuration is not set, it returns 0.00.
        """
        if not self.config:
            return Decimal('0.00')

        if self.referral.bonus_awarded:
            return Decimal('0.00')

        return self.config.first_order_bonus if self.can_award_bonus() else Decimal('0.00')
    

    def get_referral_discount(self, order: "Order") -> Decimal:
        """Returns the referral discount amount for the order if applicable."""
        if not self.config or self.referral.first_order_bonus_credited:
            return Decimal('0.00')

        # Order model uses 'client' field
        order_client = getattr(order, 'client', None) or getattr(order, 'user', None)
        if not order_client or order_client != self.referral.referee:
            return Decimal('0.00')

        previous_orders = order_client.orders_as_client.exclude(id=order.id).filter(status='completed')
        if previous_orders.exists():
            return Decimal('0.00')

        if self.config.first_order_discount_type == 'percentage':
            discount = (self.config.first_order_discount_amount / Decimal('100')) * order.total
        else:
            discount = min(self.config.first_order_discount_amount, order.total)

        return discount 
    
    def _create_wallet_transaction(self, order, discount_amount):
        """Creates a wallet transaction for the referrer when the discount is applied."""
        # Create wallet transaction for the referrer
        wallet, created = Wallet.objects.get_or_create(user=self.referrer)
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='referral_bonus',
            amount=discount_amount,
            description=f"Referral Bonus: First Order Discount for {order.user.username}",
            website=self.website,
        )
    
    def reset_referral(self):
        """
        Reset the referral status, allowing the bonus to be re-awarded.
        """
        self.referral.bonus_awarded = False
        self.referral.first_order_bonus_credited = False
        self.referral.save()


    def get_referral_details(self):
        """
        Returns the details of the referral including referrer, referee, and bonus status.
        """
        return {
            'referrer': self.referral.referrer.username,
            'referee': self.referral.referee.username,
            'bonus_awarded': self.referral.bonus_awarded,
            'first_order_bonus_credited': self.referral.first_order_bonus_credited,
            'config': {
                'first_order_bonus': self.config.first_order_bonus if self.config else None,
                'first_order_discount_type': self.config.first_order_discount_type if self.config else None,
                'first_order_discount_amount': self.config.first_order_discount_amount if self.config else None,
            }
        }
    @staticmethod 
    def record_referral_for_user(user, request):
        """
        Record a referral for the user based on the referral code.
        Checks in this order:
        1. Request data (referral_code parameter)
        2. Query parameters (ref parameter)
        3. Session (referral_code)
        4. Pending invitations (by email)
        
        This method validates the code and creates a Referral object if valid and not a self-referral.
        """
        # Try to get code from multiple sources
        code = None
        if hasattr(request, 'data') and request.data:
            code = request.data.get("referral_code")
        if not code and hasattr(request, 'query_params') and request.query_params:
            code = request.query_params.get("ref")
        if not code and hasattr(request, 'session'):
            code = request.session.pop("referral_code", None)
        
        if not code:
            # Check if there's a pending invitation for this user's email
            from .models import PendingReferralInvitation
            pending_invitation = PendingReferralInvitation.objects.filter(
                referee_email=user.email.lower(),
                converted=False
            ).first()
            if pending_invitation:
                code = pending_invitation.referral_code

        if not code:
            return

        try:
            ref_code = ReferralCode.objects.get(code__iexact=code)
        except ReferralCode.DoesNotExist:
            return

        # Don't allow self-referral
        if ref_code.user == user:
            return

        # Check if referral already exists
        existing_referral = Referral.objects.filter(
            referrer=ref_code.user,
            referee=user,
            website=ref_code.website,
            is_deleted=False
        ).first()
        
        if existing_referral:
            return  # Already referred

        # Get IP addresses from request
        def get_client_ip(request):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
            return ip
        
        referrer_ip = get_client_ip(request) if hasattr(request, 'META') else None
        referee_ip = referrer_ip  # Same IP for now, will be updated when referee registers
        
        # Create the referral
        referral = Referral.objects.create(
            website=ref_code.website,
            referrer=ref_code.user,
            referee=user,
            referral_code=code,
            referrer_ip=referrer_ip,
            referee_ip=referee_ip
        )
        
        # Run abuse detection
        try:
            from referrals.services.abuse_detection import ReferralAbuseDetectionService
            ReferralAbuseDetectionService.check_all_abuse_patterns(referral)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Abuse detection error (non-blocking): {e}", exc_info=True)

        # Check if there's a pending invitation for this email and mark it as converted
        from .models import PendingReferralInvitation
        pending_invitation = PendingReferralInvitation.objects.filter(
            referee_email=user.email.lower(),
            referral_code=code,
            converted=False
        ).first()
        
        if pending_invitation:
            pending_invitation.mark_as_converted()


    def update_stats(self, bonus_amount, successful):
        """Updates referral stats when a bonus is awarded."""
        self.total_referrals += 1
        if successful:
            self.successful_referrals += 1
            self.referral_bonus_earned += bonus_amount
        self.last_referral_at = now()
        self.save()