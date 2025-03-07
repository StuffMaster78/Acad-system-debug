from core.celery import shared_task
from django.utils.timezone import now, timedelta
from django.db import transaction
from django.db.models import Sum
from django.core.mail import send_mail
from django.conf import settings
from .models import PaymentConfirmation, ScheduledWriterPayment, WriterWallet, WriterPayment, WriterPaymentBatch, WalletTransaction


@shared_task
def auto_approve_pending_payments():
    """
    Auto-approve pending payments if the writer does not confirm within 24 hours.
    """
    threshold = now() - timedelta(hours=24)
    pending_confirmations = PaymentConfirmation.objects.filter(confirmed=False, requested_review=False, auto_approved_at__isnull=True, created_at__lte=threshold)

    for confirmation in pending_confirmations:
        confirmation.confirmed = True
        confirmation.auto_approved_at = now()
        confirmation.save()


@shared_task
def send_payment_reminders():
    """
    Sends reminders to writers to confirm their pending payments.
    """
    pending_confirmations = PaymentConfirmation.objects.filter(confirmed=False, requested_review=False)

    for confirmation in pending_confirmations:
        writer = confirmation.writer_wallet.writer
        send_mail(
            subject="Payment Confirmation Reminder",
            message=f"Dear {writer.username}, please confirm your pending payment.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[writer.email],
            fail_silently=True,
        )


@shared_task
def process_scheduled_payments():
    """
    Processes payments based on scheduled payment cycles (bi-weekly/monthly).
    """
    today = now().date()
    scheduled_payments = ScheduledWriterPayment.objects.filter(batch__scheduled_date=today, status="Pending")

    for payment in scheduled_payments:
        with transaction.atomic():
            writer_wallet = payment.writer_wallet
            writer_wallet.balance -= payment.amount  # Deduct from wallet
            writer_wallet.save()
            payment.status = "Paid"
            payment.payment_date = now()
            payment.save()


@shared_task
def generate_payment_batches():
    """
    Runs every 2 weeks and on the 1st of the month to generate pending payments.
    """
    today = now().date()
    
    # Determine if today is a payment cycle day
    latest_batch = WriterPaymentBatch.objects.order_by("-created_at").first()
    
    is_biweekly = (
        latest_batch and (today - latest_batch.created_at.date()).days >= 14
    )  # Ensures exactly 14 days have passed
    is_monthly = today.day == 1  # 1st of the month

    if is_biweekly or is_monthly:
        batch = WriterPaymentBatch.objects.create()  # Create a new batch

        for wallet in WriterWallet.objects.all():
            last_payment_date = latest_batch.created_at.date() if latest_batch else None

            earnings = WalletTransaction.objects.filter(
                writer_wallet=wallet,
                transaction_type="Earning",
                created_at__gt=last_payment_date if last_payment_date else None,
                created_at__lte=today,
            ).aggregate(total=Sum("amount"))["total"] or 0

            if earnings > 0:
                WriterPayment.objects.create(
                    batch=batch,
                    writer_wallet=wallet,
                    amount=earnings,
                )

        return f"Payment batch {batch.reference_code} created."
    
    return "No batch created today."