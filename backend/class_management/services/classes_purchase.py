"""Service functions for handling class purchases."""

from django.utils import timezone
from django.db import transaction

from class_management.models import ClassPurchase
from class_management.services.pricing import get_class_price
from class_management.services.installments import schedule_installments
from wallet.services import charge_wallet, InsufficientBalanceError


def handle_purchase_request(user, data):
    """Handles a one-time payment class bundle purchase."""
    program = data['program']
    duration = data['duration_weeks']
    bundle_size = data['bundle_size']

    price = get_class_price(program, duration, bundle_size)

    with transaction.atomic():
        purchase = ClassPurchase.objects.create(
            client=user,
            program=program,
            duration=duration,
            bundle_size=bundle_size,
            price_locked=price,
            status='pending'
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


def create_installment_purchase(user, data):
    """Creates a class purchase with scheduled installment payments."""
    program = data['program']
    duration = data['duration_weeks']
    bundle_size = data['bundle_size']
    num_installments = data.get('installments', 4)

    price = get_class_price(program, duration, bundle_size)

    with transaction.atomic():
        purchase = ClassPurchase.objects.create(
            client=user,
            program=program,
            duration=duration,
            bundle_size=bundle_size,
            total_price=price,
            status='pending'
        )

        schedule_installments(purchase, num_installments)

        # Optionally auto-pay first installment
        first_installment = purchase.installments.first()
        if first_installment:
            from class_management.services.installments import charge_installment
            charge_installment(user, first_installment)

        purchase.status = 'active'
        purchase.save()

    return purchase