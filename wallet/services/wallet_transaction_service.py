from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal
from wallet.models import Wallet, WalletTransaction
from wallet.exceptions import InsufficientWalletBalance


class WalletTransactionService:
    """
    Provides methods to credit, debit, and inspect wallet balances.
    Assumes WalletTransaction.wallet is linked to a Wallet, which has a .user FK.
    """
    @staticmethod
    def get_wallet(user, website):
        """
        Ensures the wallet exists for the user and website.
        """
        wallet, _ = Wallet.objects.get_or_create(user=user, website=website)
        return wallet

    @staticmethod
    def get_balance(user, website) -> Decimal:
        """
        Returns the current wallet balance for a user on a specific website.

        Args:
            user: The user whose wallet balance is being queried.
            website: The website for which the wallet balance is being queried.

        Returns:
            Decimal: Current wallet balance.
        """
        wallet = WalletTransactionService.get_wallet(user, website)
        total = wallet.transactions.aggregate(total=Sum("amount"))["total"]
        return total if total is not None else Decimal("0.00")



    @staticmethod
    @transaction.atomic
    def credit(
        user, amount, website, description="",  source="", note ="", 
        reference=None, metadata=None
    ):
        """
        Credits the user's wallet by a specified amount.

        Args:
            user: User to credit.
            amount: Amount to credit.
            reference: Optional external reference (e.g. Stripe txn ID).
            metadata: Optional JSON payload.
            description: Optional description for the transaction.
            source: Optional source of the credit (e.g. "order", "refund"). 

        Returns:
            WalletTransaction: The created credit transaction.
        """
        wallet = WalletTransactionService.get_wallet(user, website)

        return WalletTransaction.objects.create(
            wallet=wallet,
            website=website,
            description=description,
            source=source,
            note=note,
            user=user,
            amount=abs(amount),
            transaction_type="credit",
            reference=reference,
            metadata=metadata or {}
        )

    @staticmethod
    @transaction.atomic
    def debit(user, website, amount,  description="", source="", note="", reference=None, metadata=None):
        """
        Debits the user's wallet by a specified amount. Raises an error
        if funds are insufficient.

        Args:
            user: User to debit.
            amount: Amount to debit.
            reference: Optional external reference.
            metadata: Optional JSON.

        Returns:
            WalletTransaction: The created debit transaction.

        Raises:
            InsufficientWalletBalance: If wallet balance is too low.
        """
        balance = WalletTransactionService.get_balance(user, website)
        current_balance = WalletTransactionService.get_balance(user)
        if balance < amount:
            raise InsufficientWalletBalance(
                f"Insufficient funds. Current balance: {current_balance}"
            )
        
        wallet = WalletTransactionService.get_wallet(user, website)

        return WalletTransaction.objects.create(
            wallet=wallet,
            website=website,
            description=description,
            source=source,
            note=note,
            user=user,
            amount=-abs(amount),
            transaction_type="debit",
            reference=reference,
            metadata=metadata or {}
        )

    @staticmethod
    def refund(
        user, website, amount, description="", source="",
        note="", reference=None, metadata=None
    ):
        """
        Refunds a user's wallet (acts as a credit with refund intent).

        Args:
            user: User to refund.
            amount: Amount to refund.
            reference: Optional reference.
            metadata: Optional JSON.

        Returns:
            WalletTransaction: The refund credit entry.
        """
        wallet = WalletTransactionService.get_wallet(user, website)

        return WalletTransaction.objects.create(
            wallet=wallet,
            website=website,
            description=description,
            source=source,
            note=note,
            user=user,
            amount=abs(amount),
            transaction_type="refund",
            reference=reference,
            metadata=metadata or {}
        )