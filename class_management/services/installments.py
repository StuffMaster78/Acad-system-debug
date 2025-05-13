"""Service functions for handling class installment payments."""

from datetime import timedelta
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from class_management.models import ClassInstallment
from wallet.services import charge_wallet


def schedule_installments(purchase, count, interval_weeks=2):
    """Splits a total price into N installments."""
    amount = purchase.total_price / count
    for i in range(count):
        ClassInstallment.objects.create(
            purchase=purchase,
            amount=amount,
            due_date=timezone.now() + timedelta(weeks=i * interval_weeks)
        )


def charge_installment(user, installment):
    """Charges the user's wallet for a specific installment."""
    if installment.paid:
        return

    with transaction.atomic():
        charge_wallet(
            user=user,
            amount=installment.amount,
            purpose='class_installment',
            related_object=installment,
            allow_negative=True
        )

        installment.paid = True
        installment.paid_at = timezone.now()
        installment.save()

        _recalculate_purchase_payment_status(installment.purchase)


def _recalculate_purchase_payment_status(purchase):
    """Updates the paid_amount and is_fully_paid flags on the purchase."""
    total_paid = (
        purchase.installments
        .filter(paid=True)
        .aggregate(Sum("amount"))["amount__sum"]
    ) or 0

    purchase.paid_amount = total_paid
    purchase.is_fully_paid = total_paid >= purchase.total_price
    purchase.save()