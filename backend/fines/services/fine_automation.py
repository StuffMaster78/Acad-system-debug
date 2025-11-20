from django.utils import timezone
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
from orders.models import Order
from fines.models import Fine, FinePolicy, FineType, FineStatus
from fines.services.late_fine_calculation_service import LateFineCalculationService
from fines.services.fine_type_service import FineTypeService


def auto_issue_late_fine(order):
    """
    Automatically issue a lateness fine based on progressive hourly calculation.
    Uses FineTypeService for scalable fine issuance.
    Returns the Fine instance if created, or None if not applicable.
    """

    # Avoid duplicate fine
    if order.fines.filter(
        fine_type=FineType.LATE_SUBMISSION,
        fine_type_config__code='late_submission'
    ).exclude(
        status__in=[FineStatus.VOIDED, FineStatus.WAIVED]
    ).exists():
        return None  # Already fined for lateness

    # Calculate fine using progressive hourly service
    fine_amount, reason, rule = LateFineCalculationService.calculate_late_fine(order)
    
    if fine_amount is None or fine_amount <= 0:
        return None  # Not late or no fine applicable

    # Calculate hours late for progressive calculation
    deadline = order.client_deadline or order.writer_deadline
    if order.submitted_at and deadline:
        delay = order.submitted_at - deadline
        hours_late = delay.total_seconds() / 3600
    else:
        hours_late = 0
    
    # Get system user for auto-issued fines
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        system_user = User.objects.get(username='system') if hasattr(settings, 'SYSTEM_USER') else None
    except:
        system_user = None
    
    # Use FineTypeService to issue fine
    try:
        fine = FineTypeService.issue_fine(
            order=order,
            fine_type_code='late_submission',
            reason=reason,
            issued_by=system_user,
            hours_late=hours_late
        )
        return fine
    except ValueError:
        # Fallback: Fine type config not found, create fine manually
        fine = Fine.objects.create(
            order=order,
            fine_type=FineType.LATE_SUBMISSION,
            amount=fine_amount,
            reason=reason,
            issued_by=system_user,
            status=FineStatus.ISSUED,
        )
        
        # Adjust writer compensation
        from fines.services.compensation import adjust_writer_compensation
        adjust_writer_compensation(order, -fine_amount)
        
        return fine