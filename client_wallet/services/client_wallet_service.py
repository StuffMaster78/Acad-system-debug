from wallet.services.wallet_transaction_service import WalletTransactionService
from loyalty_management.services.loyalty_conversion_service import LoyaltyConversionService
from django.db import transaction
from wallet.models import Wallet
from django.core.exceptions import ValidationError

from client_management.models import ClientProfile
from referrals.models import Referral
from referrals.services.referral_stats_service import ReferralStatsService

class ClientWalletService:
    """
    Service for managing client wallet transactions.
    This service provides methods to handle various wallet transactions
    such as topping up, making payments, refunds, and loyalty conversions.
    """
    @staticmethod
    @transaction.atomic
    def top_up(wallet, amount, source=None):
        return WalletTransactionService.credit(
            wallet=wallet,
            amount=amount,
            tx_type="top_up",
            metadata={"source": source}
        )

    @staticmethod
    @transaction.atomic
    def make_payment(wallet, amount, order):
        """Deducts the specified amount from the wallet for a payment."""
        return WalletTransactionService.debit(
            wallet=wallet,
            amount=amount,
            tx_type="payment",
            reference=f"order-{order.id}",
            metadata={"order_id": order.id}
        )

    @staticmethod
    @transaction.atomic
    def refund(wallet, amount, order):
        """Credits the specified amount back to the wallet for a refund."""
        return WalletTransactionService.credit(
            wallet=wallet,
            amount=amount,
            tx_type="refund",
            reference=f"refund-{order.id}",
            metadata={"order_id": order.id}
        )

    @staticmethod
    @transaction.atomic
    def loyalty_conversion(wallet, amount, points):
        """Converts loyalty points to wallet balance.   """
        return LoyaltyConversionService.convert_points_to_wallet(
            client=wallet.user.client_profile,
            website=wallet.website,
            points=points,
            amount=amount
        )


    @staticmethod
    @transaction.atomic
    def process_split_payment(wallet, total_amount, order, external_method):
        wallet_amount = min(wallet.balance, total_amount)
        external_amount = total_amount - wallet_amount

        if wallet_amount > 0:
            ClientWalletService.make_payment(wallet, wallet_amount, order)

        return {
            "wallet_amount": wallet_amount,
            "external_method": external_method,
            "external_amount": external_amount
        }


    @staticmethod
    def handle_referral_bonus_grant(referral: Referral):
        """
        Manually invoked when a referral bonus is created.
        """
        ReferralStatsService.increment_referral_count(referral.referrer)

    @staticmethod
    def handle_referral_bonus_deletion(referral: Referral):
        """
        Manually invoked when a referral bonus is deleted.
        """
        ReferralStatsService.decrement_referral_count(referral.referrer)

    @staticmethod
    def _adjust_referral_bonus(wallet):
        """
        Called manually when wallet balance changes significantly.
        """
        # Implement threshold logic here
        balance = wallet.balance
        if balance < 10:
            pass  # maybe revoke bonus eligibility
        elif balance > 100:
            pass  # maybe issue bonus, unlock perk, etc.