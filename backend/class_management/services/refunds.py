# services/refunds.py

from orders.models import WalletTransaction
from class_management.models import ClassPurchase, ClassInstallment
from orders.services.wallet import credit_wallet

def refund_class_purchase(purchase):
    if purchase.status != 'paid':
        raise ValueError("Cannot refund unpaid purchase.")

    credit_wallet(
        user=purchase.client,
        amount=purchase.price_locked,
        purpose='class_purchase_refund',
        related_object=purchase
    )

    purchase.status = 'refunded'
    purchase.save()