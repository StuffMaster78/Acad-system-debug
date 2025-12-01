"""
Signals for integrating advance payment deductions into writer payment processing.
"""
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from writer_wallet.models import WriterPayment, ScheduledWriterPayment
from writer_management.services.advance_payment_service import AdvancePaymentService
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=WriterPayment)
def deduct_advances_from_payment(sender, instance, **kwargs):
    """
    Deduct outstanding advances from writer payment before saving.
    This ensures advances are automatically repaid from future earnings.
    """
    # Only process if payment is being created or amount is being set
    if instance.pk is None or 'amount' in instance.get_dirty_fields():
        try:
            # Process advance deductions
            remaining_amount = AdvancePaymentService.process_advance_deductions(instance)
            
            # Update the payment amount to reflect deductions
            if remaining_amount != instance.amount:
                logger.info(
                    f"Advance deductions applied to payment {instance.id or 'new'}: "
                    f"${instance.amount} -> ${remaining_amount}"
                )
                instance.amount = remaining_amount
        except Exception as e:
            logger.error(f"Error processing advance deductions for payment: {e}")
            # Don't fail the payment if advance deduction fails
            # Just log the error and continue


@receiver(pre_save, sender=ScheduledWriterPayment)
def deduct_advances_from_scheduled_payment(sender, instance, **kwargs):
    """
    Deduct outstanding advances from scheduled writer payment before saving.
    """
    # Only process if payment is being created or amount is being set
    if instance.pk is None or 'amount' in instance.get_dirty_fields():
        try:
            # Convert ScheduledWriterPayment to WriterPayment-like object for processing
            # Create a temporary WriterPayment object for the service
            from writer_wallet.models import WriterPayment
            temp_payment = WriterPayment(
                website=instance.website,
                writer_wallet=instance.writer_wallet,
                amount=instance.amount,
                status='Pending'
            )
            
            # Process advance deductions
            remaining_amount = AdvancePaymentService.process_advance_deductions(temp_payment)
            
            # Update the scheduled payment amount
            if remaining_amount != instance.amount:
                logger.info(
                    f"Advance deductions applied to scheduled payment {instance.id or 'new'}: "
                    f"${instance.amount} -> ${remaining_amount}"
                )
                instance.amount = remaining_amount
        except Exception as e:
            logger.error(f"Error processing advance deductions for scheduled payment: {e}")
            # Don't fail the payment if advance deduction fails

