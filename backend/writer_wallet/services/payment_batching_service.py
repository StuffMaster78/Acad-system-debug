"""
Service for generating payment batches based on writer preferences.
Handles bi-weekly and monthly payment schedules with proper date calculation.
"""
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Q, Exists, OuterRef
from writer_wallet.models import (
    PaymentSchedule, ScheduledWriterPayment, PaymentOrderRecord,
    WriterWallet, WalletTransaction
)
from writer_management.models.profile import WriterProfile
from orders.models import Order
from writer_management.models.tipping import Tip
from fines.models import Fine


class PaymentBatchingService:
    """
    Service to generate payment batches based on writer payment schedule preferences.
    """
    
    @staticmethod
    def calculate_payment_date(writer_profile, schedule_type, base_date=None):
        """
        Calculate the next payment date based on writer's preference.
        
        Args:
            writer_profile: WriterProfile instance
            schedule_type: 'bi-weekly' or 'monthly'
            base_date: Base date to calculate from (defaults to today)
            
        Returns:
            datetime: Next payment date
        """
        if base_date is None:
            base_date = timezone.now().date()
        
        payment_date_pref = writer_profile.payment_date_preference
        
        if schedule_type == 'bi-weekly':
            # Bi-weekly: default to 1st and 15th, or custom dates
            if payment_date_pref:
                try:
                    # Parse dates like "1,15" or "5,20"
                    dates = [int(d.strip()) for d in payment_date_pref.split(',')]
                    # Find next date from the list
                    for day in sorted(dates):
                        if day >= base_date.day:
                            return base_date.replace(day=day)
                    # If all dates passed, use first date of next month
                    next_month = base_date.replace(day=1) + timedelta(days=32)
                    return next_month.replace(day=dates[0])
                except (ValueError, AttributeError):
                    pass
            
            # Default: 1st and 15th
            if base_date.day < 15:
                return base_date.replace(day=15)
            else:
                next_month = base_date.replace(day=1) + timedelta(days=32)
                return next_month.replace(day=1)
        
        elif schedule_type == 'monthly':
            # Monthly: default to 1st, or custom date
            if payment_date_pref:
                try:
                    day = int(payment_date_pref.split(',')[0].strip())
                    if day >= base_date.day:
                        return base_date.replace(day=day)
                    # Next month
                    next_month = base_date.replace(day=1) + timedelta(days=32)
                    return next_month.replace(day=day)
                except (ValueError, AttributeError):
                    pass
            
            # Default: 1st of month
            if base_date.day == 1:
                return base_date
            next_month = base_date.replace(day=1) + timedelta(days=32)
            return next_month.replace(day=1)
        
        return base_date
    
    @staticmethod
    def get_earnings_for_period(writer_wallet, period_start, period_end, website):
        """
        Calculate total earnings for a writer in a given period.
        Only includes completed/approved earnings.
        
        Args:
            writer_wallet: WriterWallet instance
            period_start: Start of period (datetime)
            period_end: End of period (datetime)
            website: Website instance
            
        Returns:
            dict: {
                'orders': list of order earnings,
                'tips': Decimal total tips,
                'bonuses': Decimal total bonuses,
                'fines': Decimal total fines,
                'total': Decimal total earnings
            }
        """
        writer = writer_wallet.writer
        
        # Get completed orders in period
        completed_orders = Order.objects.filter(
            assigned_writer=writer.user,
            website=website,
            status__in=['completed', 'submitted'],
            completed_at__gte=period_start,
            completed_at__lte=period_end
        ).exclude(
            # Exclude orders already included in a payment
            Exists(
                PaymentOrderRecord.objects.filter(
                    order=OuterRef('pk'),
                    payment__status='Paid'
                )
            )
        )
        
        # Calculate order earnings
        order_earnings = []
        total_order_earnings = Decimal('0.00')
        
        for order in completed_orders:
            # Get writer payment for this order
            from writer_payments_management.models import WriterPayment as WriterPaymentModel
            writer_payment = WriterPaymentModel.objects.filter(
                writer=writer,
                order=order
            ).first()
            
            if writer_payment and writer_payment.amount_paid:
                amount = writer_payment.amount_paid
                order_earnings.append({
                    'order_id': order.id,
                    'order_topic': order.topic,
                    'amount': amount,
                    'completed_at': order.completed_at,
                })
                total_order_earnings += amount
        
        # Get tips in period
        tips = Tip.objects.filter(
            writer=writer.user,
            website=website,
            payment_status='completed',
            sent_at__gte=period_start,
            sent_at__lte=period_end
        )
        total_tips = sum(tip.writer_earning for tip in tips) or Decimal('0.00')
        
        # Get bonuses from wallet transactions
        bonuses = WalletTransaction.objects.filter(
            writer_wallet=writer_wallet,
            website=website,
            transaction_type='Bonus',
            created_at__gte=period_start,
            created_at__lte=period_end
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Get fines (already deducted from wallet, but track for reporting)
        fines = Fine.objects.filter(
            writer=writer,
            website=website,
            created_at__gte=period_start,
            created_at__lte=period_end,
            status__in=['active', 'paid']
        )
        total_fines = sum(fine.amount for fine in fines) or Decimal('0.00')
        
        total_earnings = total_order_earnings + total_tips + bonuses - total_fines
        
        return {
            'orders': order_earnings,
            'tips': total_tips,
            'bonuses': bonuses,
            'fines': total_fines,
            'total': total_earnings,
        }
    
    @staticmethod
    @transaction.atomic
    def generate_payment_batch(website, schedule_type, scheduled_date, processed_by=None):
        """
        Generate a payment batch for a specific schedule type and date.
        
        Args:
            website: Website instance
            schedule_type: 'Bi-Weekly' or 'Monthly'
            scheduled_date: Date when payments should be processed
            processed_by: User who is processing the batch (optional)
            
        Returns:
            PaymentSchedule: Created payment schedule with all payments
        """
        # Calculate period dates
        if schedule_type == 'Bi-Weekly':
            period_start = scheduled_date - timedelta(days=14)
            period_end = scheduled_date
        else:  # Monthly
            # Start of month
            period_start = scheduled_date.replace(day=1)
            # End of month
            if scheduled_date.month == 12:
                period_end = scheduled_date.replace(year=scheduled_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                period_end = scheduled_date.replace(month=scheduled_date.month + 1, day=1) - timedelta(days=1)
        
        # Create payment schedule
        schedule = PaymentSchedule.objects.create(
            website=website,
            schedule_type=schedule_type,
            scheduled_date=scheduled_date,
            processed_by=processed_by,
            completed=False
        )
        
        # Get all writers with matching payment schedule preference
        writers = WriterProfile.objects.filter(
            website=website,
            payment_schedule=schedule_type.lower().replace('-', '_'),
            user__is_active=True
        ).select_related('user', 'wallet')
        
        total_batch_amount = Decimal('0.00')
        
        for writer_profile in writers:
            try:
                writer_wallet = WriterWallet.objects.get(
                    writer=writer_profile.user,
                    website=website
                )
            except WriterWallet.DoesNotExist:
                continue
            
            # Get earnings for this period
            earnings_data = PaymentBatchingService.get_earnings_for_period(
                writer_wallet,
                period_start,
                period_end,
                website
            )
            
            # Only create payment if there are earnings
            if earnings_data['total'] > 0:
                # Create scheduled payment
                scheduled_payment = ScheduledWriterPayment.objects.create(
                    website=website,
                    batch=schedule,
                    writer_wallet=writer_wallet,
                    amount=earnings_data['total'],
                    status='Pending'
                )
                
                # Create order records
                for order_data in earnings_data['orders']:
                    try:
                        order = Order.objects.get(id=order_data['order_id'])
                        PaymentOrderRecord.objects.create(
                            website=website,
                            payment=scheduled_payment,
                            order=order,
                            amount_paid=order_data['amount']
                        )
                    except Order.DoesNotExist:
                        continue
                
                total_batch_amount += earnings_data['total']
        
        return schedule
    
    @staticmethod
    def get_batch_breakdown(schedule):
        """
        Get detailed breakdown of a payment batch.
        
        Args:
            schedule: PaymentSchedule instance
            
        Returns:
            dict: Detailed breakdown with all writers and line items
        """
        payments = ScheduledWriterPayment.objects.filter(
            batch=schedule
        ).select_related(
            'writer_wallet__writer__user',
            'writer_wallet__website'
        ).prefetch_related('orders__order')
        
        breakdown = {
            'schedule_id': schedule.id,
            'schedule_type': schedule.schedule_type,
            'scheduled_date': schedule.scheduled_date.isoformat(),
            'completed': schedule.completed,
            'reference_code': schedule.reference_code,
            'total_amount': Decimal('0.00'),
            'total_writers': 0,
            'writers': []
        }
        
        for payment in payments:
            if not payment.writer_wallet or not payment.writer_wallet.writer:
                continue
            
            writer = payment.writer_wallet.writer
            user = writer.user
            
            # Get order breakdown
            order_records = payment.orders.all()
            orders_breakdown = []
            for record in order_records:
                orders_breakdown.append({
                    'order_id': record.order.id,
                    'order_topic': record.order.topic or 'N/A',
                    'amount': float(record.amount_paid),
                    'completed_at': record.order.completed_at.isoformat() if record.order.completed_at else None,
                })
            
            # Get tips and fines for this period
            period_start = schedule.scheduled_date
            period_end = schedule.scheduled_date + timedelta(
                days=14 if schedule.schedule_type == 'Bi-Weekly' else 30
            )
            
            tips_total = Decimal('0.00')
            try:
                tips = Tip.objects.filter(
                    writer=user,
                    website=schedule.website,
                    sent_at__gte=period_start,
                    sent_at__lt=period_end
                )
                tips_total = sum(tip.writer_earning for tip in tips)
            except Exception:
                pass
            
            fines_total = Decimal('0.00')
            try:
                fines = Fine.objects.filter(
                    writer=writer,
                    website=schedule.website,
                    created_at__gte=period_start,
                    created_at__lt=period_end
                )
                fines_total = sum(fine.amount for fine in fines)
            except Exception:
                pass
            
            breakdown['writers'].append({
                'writer_id': writer.id,
                'writer_name': user.get_full_name() if user else writer.registration_id,
                'writer_email': user.email if user else '',
                'registration_id': writer.registration_id,
                'total_amount': float(payment.amount),
                'orders': orders_breakdown,
                'orders_count': len(orders_breakdown),
                'tips': float(tips_total),
                'fines': float(fines_total),
                'status': payment.status,
                'payment_id': payment.id,
                'reference_code': payment.reference_code,
            })
            
            breakdown['total_amount'] += payment.amount
            breakdown['total_writers'] += 1
        
        breakdown['total_amount'] = float(breakdown['total_amount'])
        
        return breakdown

