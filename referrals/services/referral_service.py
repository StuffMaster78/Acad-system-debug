import uuid
from django.db import transaction
from django.utils.timezone import now
from decimal import Decimal
from wallet.models import Wallet, WalletTransaction
from orders.models import Order
from referrals.models import Referral, ReferralCode, ReferralBonusConfig
from loyalty_management.models import LoyaltyTransaction


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

    def can_award_bonus(self) -> bool:
        if self.referral.bonus_awarded or not self.config:
            return False

        first_order = self._get_qualifying_order()
        return bool(first_order)

    def _get_qualifying_order(self):
        return self.referral.referee.orders.filter(status='completed', payment_status='paid').first()
    
    def get_referral_link(self):
        """Dynamically generates a referral link."""
        return f"https://{self.website.domain}/order?ref={self.code}"

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

    def apply_discount(self, order: Order) -> Decimal:
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

        if order.user != self.referral.referee:
            return Decimal('0.00')

        previous_orders = order.user.orders.exclude(id=order.id).filter(status='completed')
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
            description=f"Referral Discount Applied for {order.user.username}",
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
    

    def get_referral_discount(self, order: Order) -> Decimal:
        """Returns the referral discount amount for the order if applicable."""
        if not self.config or self.referral.first_order_bonus_credited:
            return Decimal('0.00')

        if order.user != self.referral.referee:
            return Decimal('0.00')

        previous_orders = order.user.orders.exclude(id=order.id).filter(status='completed')
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
    
    def record_referral_for_user(user, request):
        """
        Record a referral for the user based on the referral code stored in the session.
        This method checks if a referral code exists in the session, validates it,
        and creates a Referral object if the code is valid and not a self-referral.
        """
        code = request.session.pop("referral_code", None)
        if not code:
            return

        try:
            ref_code = ReferralCode.objects.get(code__iexact=code)
        except ReferralCode.DoesNotExist:
            return

        # Don’t allow self-referral
        if ref_code.user == user:
            return

        Referral.objects.create(
            website=ref_code.website,
            referrer=ref_code.user,
            referee=user,
            referral_code=code
        )


    def update_stats(self, bonus_amount, successful):
        """Updates referral stats when a bonus is awarded."""
        self.total_referrals += 1
        if successful:
            self.successful_referrals += 1
            self.referral_bonus_earned += bonus_amount
        self.last_referral_at = now()
        self.save()