from django.utils import timezone
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
from orders.models import Order
from fines.models import Fine, FinePolicy, FineType


def auto_issue_late_fine(order):
    """
    Automatically issue a lateness fine based on the hours/days past deadline.
    Returns the Fine instance if created, or None if not applicable.
    """

    if not order.submitted_at or not order.deadline:
        return None  # Can't evaluate lateness

    if order.submitted_at <= order.deadline:
        return None  # Submission was on time

    # Avoid duplicate fine
    if order.fines.filter(fine_type=FineType.LATE_SUBMISSION).exists():
        return None  # Already fined for lateness

    delay = order.submitted_at - order.deadline
    hours_late = delay.total_seconds() / 3600
    days_late = delay.days

    # Fallback percentage logic
    if 1 <= hours_late < 2:
        percentage = 5
    elif 2 <= hours_late < 3:
        percentage = 10
    elif 3 <= hours_late < 24:
        percentage = 15 + int(hours_late - 3) * 2
    else:
        percentage = 50 + days_late * 10  # Escalates daily

    
    # Try loading an active FinePolicy override
    policy = FinePolicy.objects.filter(
        fine_type=FineType.LATE_SUBMISSION,
        active=True,
        start_date__lte=timezone.now()
    ).order_by("-start_date").first()

    if policy and policy.fixed_amount:
        fine_amount = policy.fixed_amount
    elif policy and policy.percentage:
        percentage = Decimal(policy.percentage)
        fine_amount = (percentage / 100) * order.price
    else:
        fine_amount = (Decimal(percentage) / 100) * order.price

    fine_amount = fine_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    fine = Fine.objects.create(
        order=order,
        fine_type=FineType.LATE_SUBMISSION,
        amount=fine_amount,
        reason=(
            f"Auto-issued lateness fine: {round(hours_late, 2)}h "
            f"({round(days_late, 1)}d) late"
        ),
        issued_by=settings.SYSTEM_USER,
    )

    return fine