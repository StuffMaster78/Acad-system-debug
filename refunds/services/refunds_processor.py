from django.utils import timezone
from django.core.exceptions import ValidationError
from refunds.models import Refund
from writer_payments_management.models import WriterPayment
from writer_management.models import WriterLevel
from order_payments_management.models import AdminLog, PaymentLog
from refunds.models import RefundLog
from discounts.services.discount_usage_tracker import DiscountUsageTracker
from refunds.models import RefundReceipt
from notifications_system.services.dispatcher import notify_user
from django.db import transaction as transaction

@transaction.atomic
def process_refund(refund, processed_by, reason=None, admin_user=None):
    """
    Handles wallet/external refunds, full/partial logic, and writer deduction.
    """
    # --- Validation ---
    if refund.status != Refund.PENDING:
        raise ValidationError("Refund already processed.")

    if refund.total_amount() <= 0:
        raise ValidationError("Refund amount must be greater than zero.")

    if refund.order_payment.discounted_amount <= 0:
        raise ValidationError("Order payment amount must be greater than zero.")

    if refund.total_amount() > refund.order_payment.discounted_amount:
        raise ValidationError("Refund exceeds paid amount.")

    if refund.order_payment.order.status == 'refunded':
        raise ValidationError("Order already refunded.")

    if refund.order_payment.order.cancelled:
        raise ValidationError("Order is cancelled, cannot process refund.")

    # --- Refund to client wallet ---
    if refund.wallet_amount > 0:
        wallet = refund.client.wallet
        wallet.balance += refund.wallet_amount
        wallet.save()

    # --- Refund to external payment method (card/gateway) ---
    if refund.external_amount > 0 and refund.refund_method == "external":
        # Trigger external refund logic here (API call or webhook)
        AdminLog.log_action(
            admin=admin_user,
            action="External Refund Recorded",
            details=(
                f"${refund.external_amount} marked as refunded for client "
                f"{refund.client.username}"
            )
        )

    # --- Mark refund as processed ---
    refund.status = Refund.PROCESSED
    refund.processed_by = processed_by
    refund.processed_at = timezone.now()
    refund.save()

    # --- Create a receipt for the refund if none exists ---
    if not hasattr(refund, 'receipt'):
        RefundReceipt.objects.create(
            refund=refund,
            amount=refund.total_amount(),
            processed_by=processed_by,
            website=refund.website,
            order_payment=refund.order_payment,
            reason=reason or "Refunded"
        )

    # --- Log the refund action ---
    RefundLog.objects.create(
        website=refund.website,
        order=refund.order_payment.order,
        refund=refund,
        client=refund.client,
        processed_by=processed_by,
        action='Refund Processed',
        amount=refund.total_amount(),
        source=refund.refund_method,
        status=refund.status,
        metadata={
            'refund_id': refund.id,
            'reason': reason or "Refunded"
        }
    )

    # --- Untrack discount for full refunds ---
    if refund.total_amount() >= refund.order_payment.discounted_amount:
        DiscountUsageTracker.untrack(refund.order_payment.order)

    # --- Deduct writer earnings (only for full refunds) ---
    is_full_refund = refund.total_amount() >= refund.order_payment.discounted_amount
    assigned_writer = getattr(refund.order_payment.order, "assigned_writer", None)
    if is_full_refund and admin_user and assigned_writer:
        deduct_writer_earnings(refund, admin_user)

    # --- Log the refund event for payment logs ---
    PaymentLog.log_event(
        refund.payment,
        "Refund Processed",
        f"Refund of ${refund.total_amount()} processed."
    )

    # --- Mark order as refunded if this is a full refund ---
    if refund.total_amount() >= refund.order_payment.discounted_amount:
        mark_order_refunded(
            order=refund.order_payment.order,
            amount=refund.total_amount(),
            refund=refund,
            source=refund.refund_method,
            metadata={'reason': reason or "Refunded"}
        )

    # --- Notify the client about the refund ---
    notify_user(
        recipient=refund.client,
        title="Refund Processed",
        message=(
            f"Your refund of ${refund.total_amount()} has been processed. "
            f"Reason: {reason or 'Refunded'}."
        ),
        performed_by=processed_by,
        website=refund.website,
        extra_data={
            'refund_id': refund.id,
            'order_id': refund.order_payment.order.id,
            'amount': refund.total_amount(),
            'reason': reason or "Refunded"
        },
        category='in_app',
        channels=['in_app', 'email']
    )

@transaction.atomic
def deduct_writer_earnings(refund, admin_user):
    """
    Deducts writer earnings proportional to the refunded amount for a full refund.
    Assumes fines are handled elsewhere.

    Args:
        refund: Refund instance (must be for a full refund).
        admin_user: Admin user performing the deduction.

    Returns:
        None
    """
    order = refund.payment.order
    writer = getattr(order, "assigned_writer", None)
    if not writer:
        return

    writer_payment = WriterPayment.objects.filter(
        order=order, writer=writer
    ).first()
    if not writer_payment:
        return

    writer_level = getattr(writer, "writer_level", None)
    if not writer_level:
        raise ValidationError("Writer level is not defined.")

    # Compute writer's total earnings for this order
    earnings_per_page = getattr(writer_level, "base_pay_per_page", 0)
    earnings_per_slide = getattr(writer_level, "base_pay_per_slide", 0)
    total_writer_earnings = (
        earnings_per_page * getattr(order, "pages", 0) +
        earnings_per_slide * getattr(order, "slides", 0)
    )

    # Calculate the refund ratio and deduction
    paid_amount = refund.payment.discounted_amount
    if paid_amount == 0:
        raise ValidationError("Order payment amount is zero; cannot deduct earnings.")

    refund_ratio = refund.total_amount() / paid_amount
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

    # Notify the writer about the deduction
    notify_user(
        recipient=writer,
        title="Earnings Deduction Due to Refund",
        message=(
            f"Your earnings for Order {order.id} have been reduced by "
            f"${deduction:.2f} due to a refund processed for the order."
        ),
        performed_by=admin_user,
        website=refund.website,
        extra_data={
            'refund_id': refund.id,
            'order_id': order.id,
            'deduction': deduction
        },
        category='in_app',
        channels=['in_app', 'email']
    )

@transaction.atomic
def mark_order_refunded(
    order, amount, refund,
    source='manual', metadata=None
):
    """
    Marks an order as refunded, logs the refund, and untracks discounts if full refund.

    Args:
        order: The order instance to mark as refunded.
        amount: The refunded amount.
        refund: The Refund instance tied to this operation.
        source: Origin of the refund (manual, stripe-webhook, etc.).
        metadata: Optional dictionary with extra refund data.

    Returns:
        bool: True if order marked, False if already refunded.
    """
    # --- Validation ---
    if order.status == 'refunded':
        return False

    if amount <= 0:
        raise ValidationError("Refunded amount must be greater than zero.")

    if hasattr(order, "payment") and amount > order.payment.discounted_amount:
        raise ValidationError("Refunded amount exceeds original payment.")

    # --- Mark the order as refunded and cancelled ---
    order.status = 'refunded'
    order.cancelled = True
    order.refunded_at = timezone.now()
    order.save(update_fields=['status', 'cancelled', 'refunded_at'])

    # --- Log the refund action ---
    RefundLog.objects.create(
        website=getattr(order, "website", None),
        order=order,
        refund=refund,
        client=getattr(order, "client", None),
        processed_by=getattr(refund, "processed_by", None),
        action='Order Marked Refunded',
        amount=amount,
        source=source,
        status='success',
        metadata=metadata or {}
    )

    # --- Untrack discounts for full refunds to allow reuse ---
    if hasattr(order, "payment") and amount >= order.payment.discounted_amount:
        DiscountUsageTracker.untrack(order)

    return True