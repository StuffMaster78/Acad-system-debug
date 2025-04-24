from django.utils import timezone
from django.core.exceptions import ValidationError
from refunds.models import Refund
from writer_payments_management.models import WriterPayment
from writer_management.models import WriterLevel
from order_payments_management.models import AdminLog, PaymentLog
from refunds.models import RefundLog

def process_refund(refund, admin_user):
    """
    Handles full refund logic—wallet, external logging, writer deduction.
    """
    if refund.status != Refund.PENDING:
        raise ValidationError("Refund already processed.")

    if refund.total_amount() > refund.order_payment.discounted_amount:
        raise ValidationError("Refund exceeds paid amount.")
    

    if refund.refund_method == "external":
        raise ValidationError("External retry not supported.")

    # Process wallet part
    if refund.wallet_amount > 0:
        wallet = refund.client.wallet
        wallet.balance += refund.wallet_amount
        wallet.save()

    # Manual logging for external refunds
    if refund.external_amount > 0 and refund.refund_method == "external":
        AdminLog.log_action(
            admin=admin_user,
            action="External Refund Recorded",
            details=(
                f"${refund.external_amount} marked as refunded for client "
                f"{refund.client.username}"
            )
        )

    # Mark refund as processed
    refund.status = Refund.PROCESSED
    refund.processed_by = admin_user
    refund.processed_at = timezone.now()
    refund.save()

    deduct_writer_earnings(refund, admin_user)

    # Log the refund event for payment logs
    PaymentLog.log_event(
        refund.payment,
        "Refund Processed",
        f"Refund of ${refund.total_amount()} processed."
    )


def deduct_writer_earnings(refund, admin_user):
    """
    Deduct writer earnings proportional to the refunded amount.
    Assumes fines are handled elsewhere.
    """
    order = refund.payment.order
    writer = order.assigned_writer
    if not writer:
        return

    writer_payment = WriterPayment.objects.filter(
        order=order, writer=writer
    ).first()
    if not writer_payment:
        return

    # Fetch the writer's level and pay rate information
    writer_level = writer.writer_level
    if not writer.writer_level:
        raise ValidationError("Writer level is not defined.")

    # Compute writer's total earnings for this order
    # based on their writer level
    earnings_per_page = writer_level.base_pay_per_page
    earnings_per_slide = writer_level.base_pay_per_slide

    total_writer_earnings = (
        earnings_per_page * order.pages +
        earnings_per_slide * order.slides
    )

    # Calculate the refund ratio
    refund_ratio = refund.total_amount() / refund.payment.discounted_amount
    deduction = total_writer_earnings * refund_ratio

    # Deduct writer's earnings
    writer_payment.amount_paid -= deduction
    writer_payment.save()

    # Log the writer deduction
    AdminLog.log_action(
        admin=admin_user,
        action="Writer Refund Deduction",
        details=(
            f"Deducted ${deduction:.2f} from writer {writer.username} "
            f"due to a refund on Order {order.id}."
        )
    )


def mark_order_refunded(order, amount, source='manual', metadata=None):
    """
    Marks an order as refunded and logs the refund.

    Args:
        order: The order instance to mark as refunded.
        amount: The refunded amount.
        source: Origin of the refund (manual, stripe-webhook, etc.).
        metadata: Optional dictionary with extra refund data.

    Returns:
        bool: True if order marked, False if already refunded.
    """
    if order.status == 'refunded':
        return False

    # Mark the order as refunded and cancelled
    order.status = 'refunded'
    order.cancelled = True
    order.refunded_at = timezone.now()
    order.save(update_fields=['status', 'cancelled', 'refunded_at'])

    # Log the refund action
    RefundLog.objects.create(
        order=order,
        amount=amount,
        source=source,
        status='success',
        metadata=metadata or {}
    )

    return True