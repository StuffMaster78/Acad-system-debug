"""
Streamlined Class Payment Service
Handles class payments, installments, and writer compensation in a unified way.
"""
import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from class_management.class_payment import (
    ClassPayment,
    ClassPaymentInstallment,
    ClassWriterPayment,
)
from class_management.models import ClassBundle, ClassInstallment
from special_orders.models import WriterBonus

logger = logging.getLogger(__name__)


class ClassPaymentService:
    """
    Service for managing class payments and installments.
    """
    
    @staticmethod
    @transaction.atomic
    def create_payment_for_bundle(bundle: ClassBundle, writer=None):
        """
        Create a ClassPayment record for a class bundle.
        This should be called when a bundle is created or when a writer is assigned.
        """
        # Check if payment already exists
        existing_payment = ClassPayment.objects.filter(class_bundle=bundle).first()
        if existing_payment:
            # Update writer if provided
            if writer:
                existing_payment.assigned_writer = writer
                existing_payment.writer_compensation_amount = existing_payment.calculate_writer_compensation()
                existing_payment.save()
            return existing_payment
        
        # Calculate amounts
        total_amount = bundle.total_price or Decimal('0.00')
        deposit_amount = bundle.deposit_required or Decimal('0.00')
        deposit_paid = bundle.deposit_paid or Decimal('0.00')
        balance_remaining = bundle.balance_remaining or total_amount
        
        # Create payment record
        payment = ClassPayment.objects.create(
            class_bundle=bundle,
            website=bundle.website,
            assigned_writer=writer or bundle.assigned_writer,
            total_amount=total_amount,
            deposit_amount=deposit_amount,
            deposit_paid=deposit_paid,
            balance_remaining=balance_remaining,
            uses_installments=bundle.installments_enabled,
            total_installments=bundle.installment_count or 0,
        )
        
        # Calculate writer compensation
        payment.writer_compensation_amount = payment.calculate_writer_compensation()
        payment.save()
        
        # Link existing installments if any
        if bundle.installments_enabled:
            ClassPaymentService._link_installments(payment, bundle)
        
        logger.info(f"Created ClassPayment {payment.id} for bundle {bundle.id}")
        return payment
    
    @staticmethod
    def _link_installments(payment: ClassPayment, bundle: ClassBundle):
        """Link existing ClassInstallments to ClassPayment."""
        installments = ClassInstallment.objects.filter(class_bundle=bundle).order_by('installment_number')
        
        for installment in installments:
            payment_installment, created = ClassPaymentInstallment.objects.get_or_create(
                class_payment=payment,
                class_installment=installment,
                defaults={
                    'installment_number': installment.installment_number or 0,
                    'amount': installment.amount,
                    'is_paid': installment.is_paid,
                    'paid_at': installment.paid_at,
                    'payment_record': installment.payment_record,
                }
            )
            
            if not created:
                # Update if installment status changed
                payment_installment.is_paid = installment.is_paid
                payment_installment.paid_at = installment.paid_at
                payment_installment.payment_record = installment.payment_record
                payment_installment.save()
    
    @staticmethod
    @transaction.atomic
    def record_installment_payment(installment: ClassInstallment, payment_record):
        """
        Record an installment payment and update ClassPayment status.
        """
        # Find the ClassPayment for this bundle
        try:
            class_payment = ClassPayment.objects.get(class_bundle=installment.class_bundle)
        except ClassPayment.DoesNotExist:
            # Create payment if it doesn't exist
            class_payment = ClassPaymentService.create_payment_for_bundle(installment.class_bundle)
        
        # Update or create payment installment link
        payment_installment, created = ClassPaymentInstallment.objects.get_or_create(
            class_payment=class_payment,
            class_installment=installment,
            defaults={
                'installment_number': installment.installment_number or 0,
                'amount': installment.amount,
            }
        )
        
        # Update payment installment
        payment_installment.is_paid = installment.is_paid
        payment_installment.paid_at = installment.paid_at
        payment_installment.payment_record = payment_record
        payment_installment.save()
        
        # Update class payment status
        ClassPaymentService._update_payment_status(class_payment)
        
        logger.info(f"Recorded installment payment for installment {installment.id}")
        return payment_installment
    
    @staticmethod
    def _update_payment_status(payment: ClassPayment):
        """Update payment status based on installments and payments."""
        bundle = payment.class_bundle
        
        # Update deposit paid
        payment.deposit_paid = bundle.deposit_paid or Decimal('0.00')
        
        # Calculate balance from installments
        paid_installments = ClassPaymentInstallment.objects.filter(
            class_payment=payment,
            is_paid=True
        )
        total_paid = sum(pi.amount for pi in paid_installments)
        payment.balance_remaining = payment.total_amount - total_paid - payment.deposit_paid
        payment.paid_installments = paid_installments.count()
        
        # Update statuses
        payment.update_client_payment_status()
        
        # If fully paid and writer assigned, schedule writer payment
        if payment.is_fully_paid and payment.assigned_writer and not payment.is_writer_paid:
            ClassPaymentService._schedule_writer_payment(payment)
        
        payment.save()
    
    @staticmethod
    @transaction.atomic
    def _schedule_writer_payment(payment: ClassPayment):
        """
        Schedule writer payment when class bundle is fully paid.
        Creates WriterBonus if needed.
        """
        if payment.writer_payment_status == 'paid':
            return
        
        # Check if writer bonus already exists
        existing_bonus = WriterBonus.objects.filter(
            writer=payment.assigned_writer,
            category='class_payment',
            special_order=None,
        ).first()
        
        if not existing_bonus and payment.writer_compensation_amount > 0:
            # Create WriterBonus
            bonus = WriterBonus.objects.create(
                website=payment.website,
                writer=payment.assigned_writer,
                special_order=None,
                amount=payment.writer_compensation_amount,
                category='class_payment',
                reason=f"Payment for Class Bundle #{payment.class_bundle.id}",
                is_paid=False,
            )
            
            # Create ClassWriterPayment record
            ClassWriterPayment.objects.create(
                class_payment=payment,
                writer_bonus=bonus,
                amount=payment.writer_compensation_amount,
                payment_type='full',
                is_paid=False,
            )
            
            payment.writer_payment_status = 'scheduled'
            payment.save()
            
            logger.info(f"Scheduled writer payment ${payment.writer_compensation_amount} for bundle {payment.class_bundle.id}")
    
    @staticmethod
    def get_payment_details(bundle_id):
        """
        Get comprehensive payment details for a class bundle.
        Returns payment, installments, and writer payment info.
        """
        try:
            bundle = ClassBundle.objects.get(id=bundle_id)
        except ClassBundle.DoesNotExist:
            return None
        
        # Get or create payment
        payment = ClassPayment.objects.filter(class_bundle=bundle).first()
        if not payment:
            payment = ClassPaymentService.create_payment_for_bundle(bundle)
        
        # Get installments
        installments = ClassPaymentInstallment.objects.filter(
            class_payment=payment
        ).select_related('class_installment', 'payment_record').order_by('installment_number')
        
        # Get writer payments
        writer_payments = ClassWriterPayment.objects.filter(
            class_payment=payment
        ).select_related('writer_bonus').order_by('-created_at')
        
        return {
            'payment': payment,
            'installments': installments,
            'writer_payments': writer_payments,
        }
    
    @staticmethod
    def get_writer_class_payments(writer):
        """
        Get all class payments for a writer with installment details.
        """
        payments = ClassPayment.objects.filter(
            assigned_writer=writer
        ).select_related('class_bundle', 'website').prefetch_related(
            'payment_installments__class_installment',
            'writer_payments__writer_bonus'
        ).order_by('-created_at')
        
        return payments

