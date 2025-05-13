from django.utils import timezone
from orders.services.wallet import charge_wallet, InsufficientBalanceError
from django.db import transaction
from orders.models import WalletTransaction
from class_management.models import ClassPurchase, Class

# services/class_purchases.py
from .pricing import get_class_price  # your pricing table logic
from wallet.services import charge_wallet

def handle_purchase_request(user, data, website):
    program = data['program']
    duration = data['duration_weeks']
    bundle_size = data['bundle_size']

    price = get_class_price(program, duration, bundle_size, website)

    purchase = ClassPurchase.objects.create(
        client=user,
        program=program,
        duration=duration,
        bundle_size=bundle_size,
        price_locked=price,
        status='pending',
        website=website
    )

    charge_wallet(
        user=user,
        amount=price,
        purpose='class_purchase',
        related_object=purchase,
        allow_negative=True
    )

    purchase.status = 'paid'
    purchase.paid_at = timezone.now()
    purchase.save()

    return purchase

def create_class_purchase(user, data):
    price = get_class_price(...)  # as before
    num_installments = data['installments']  # e.g., 4

    purchase = ClassPurchase.objects.create(
        client=user,
        total_price=price,
        status='pending'
    )

    # Split into equal installments
    installment_amount = price / num_installments
    for i in range(num_installments):
        ClassInstallment.objects.create(
            purchase=purchase,
            amount=installment_amount,
            due_date=timezone.now() + timedelta(weeks=2 * i)
        )

    # Optionally auto-pay first installment
    charge_installment(user, purchase.installments.first())

    purchase.status = 'active'
    purchase.save()
    return purchase

def charge_installment(user, installment):
    charge_wallet(
        user=user,
        amount=installment.amount,
        purpose='class_installment',
        related_object=installment,
        allow_negative=True
    )
    installment.paid = True
    installment.paid_at = timezone.now()
    installment.wallet_txn = last_wallet_txn(user)  # your logic
    installment.save()

    # Recalc ClassPurchase
    purchase = installment.purchase
    purchase.paid_amount = purchase.installments.filter(paid=True).aggregate(Sum("amount"))["amount__sum"] or 0
    purchase.is_fully_paid = purchase.paid_amount >= purchase.total_price
    purchase.save()



def charge_wallet(user, amount, purpose, related_object=None, allow_negative=True):
    wallet = user.wallet

    if not allow_negative and wallet.balance < amount:
        raise InsufficientBalanceError("Insufficient funds.")

    with transaction.atomic():
        wallet.balance -= amount
        wallet.save()

        WalletTransaction.objects.create(
            user=user,
            amount=-amount,  # Deduction
            purpose=purpose,
            related_object=related_object
        )

    return wallet.balance


def process_class_purchase(purchase):
    user = purchase.client
    amount = purchase.price_locked

    try:
        charge_wallet(user, amount, purpose='class_purchase', related_object=purchase)
    except InsufficientBalanceError:
        raise ValueError("Insufficient wallet balance. Please top up.")

    purchase.status = 'paid'
    purchase.paid_at = timezone.now()
    purchase.save()

def process_class_purchase(purchase):
    user = purchase.client
    amount = purchase.price_locked

    # Wallet charge: allows negative
    charge_wallet(user, amount, purpose='class_purchase', related_object=purchase)

    purchase.status = 'paid'
    purchase.paid_at = timezone.now()
    purchase.save()


def credit_wallet(user, amount, purpose, related_object=None):
    wallet = user.wallet
    with transaction.atomic():
        wallet.balance += amount
        wallet.save()

        WalletTransaction.objects.create(
            user=user,
            amount=amount,
            purpose=purpose,
            related_object=related_object
        )

    return wallet.balance
