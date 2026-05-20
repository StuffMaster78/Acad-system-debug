from wallet.services.wallet_transaction_service import WalletTransactionService


class WriterWalletService:
    """
    Service for managing writer wallet transactions.
    This service provides methods to handle various wallet transactions
    such as crediting payments, applying fines, bonuses, and payouts.
    """
    @staticmethod
    def credit_order_payment(wallet, amount, order):
        return WalletTransactionService.credit(
            user=wallet.writer,
            website=wallet.website,
            amount=amount,
            transaction_type="order_payment",
            reference=f"order-{order.id}",
            source="writer_wallet",
            metadata={"order_id": order.id}
        )

    @staticmethod
    def apply_fine(wallet, amount, reason):
        return WalletTransactionService.debit(
            user=wallet.writer,
            website=wallet.website,
            amount=abs(amount),
            transaction_type="fine",
            source="writer_wallet",
            metadata={"reason": reason}
        )

    @staticmethod
    def apply_bonus(wallet, amount, note=None):
        return WalletTransactionService.credit(
            user=wallet.writer,
            website=wallet.website,
            amount=amount,
            transaction_type="bonus",
            source="writer_wallet",
            metadata={"note": note}
        )

    @staticmethod
    def payout(wallet, amount, batch=None):
        return WalletTransactionService.debit(
            user=wallet.writer,
            website=wallet.website,
            amount=amount,
            transaction_type="payout",
            source="writer_wallet",
            metadata={"batch_id": batch.id if batch else None}
        )
    @staticmethod
    def credit_order_payment_with_metadata(wallet, amount, order, metadata):
        return WalletTransactionService.credit(
            user=wallet.writer,
            website=wallet.website,
            amount=amount,
            transaction_type="order_payment",
            reference=f"order-{order.id}",
            source="writer_wallet",
            metadata={**{"order_id": order.id}, **metadata}
        )
    @staticmethod
    def apply_fine_with_metadata(wallet, amount, reason, metadata):
        return WalletTransactionService.debit(
            user=wallet.writer,
            website=wallet.website,
            amount=abs(amount),
            transaction_type="fine",
            source="writer_wallet",
            metadata={**{"reason": reason}, **metadata}
        )
    @staticmethod
    def deduct_amount(wallet, amount, reason):
        """
        Deducts a specified amount from the wallet with a reason.
        This is a general method for any deduction that doesn't fit
        into the other specific transaction types.
        """
        return WalletTransactionService.debit(
            user=wallet.writer,
            website=wallet.website,
            amount=abs(amount),
            transaction_type="deduction",
            source="writer_wallet",
            metadata={"reason": reason}
        )
    
