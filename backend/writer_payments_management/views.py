from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from calendar import monthrange

from .models import WriterPayment, WriterPayoutRequest, WriterPaymentAdjustment
from writer_wallet.models import PaymentSchedule, ScheduledWriterPayment
from writer_management.models import WriterProfile
from websites.models import Website
from django.contrib.auth import get_user_model
from admin_management.permissions import IsAdmin

User = get_user_model()


class WriterPaymentManagementViewSet(viewsets.ViewSet):
    """
    Comprehensive payment management endpoints for admin/superadmin.
    Handles payment adjustments, moving to next period, clearing payments, etc.
    """
    permission_classes = [IsAdmin]

    @action(detail=True, methods=['post'], url_path='move-to-next-period')
    def move_to_next_period(self, request, pk=None):
        """
        Move a payment to the next payment period with a reason.
        
        Body:
        - reason: str (required) - Reason for moving the payment
        - target_period_type: str (optional) - 'biweekly' or 'monthly' (default: same as current)
        """
        try:
            payment = WriterPayment.objects.get(pk=pk)
        except WriterPayment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        reason = request.data.get('reason', '')
        if not reason:
            return Response(
                {'error': 'Reason is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        target_period_type = request.data.get('target_period_type', None)

        with transaction.atomic():
            # Create adjustment record
            adjustment = WriterPaymentAdjustment.objects.create(
                website=payment.website,
                writer_payment=payment,
                admin=request.user,
                adjustment_amount=-payment.amount,  # Negative to remove from current period
                reason=f"Moved to next period: {reason}"
            )

            # If payment was already paid, create a negative adjustment
            if payment.status == 'Paid':
                # Create negative payment entry
                negative_payment = WriterPayment.objects.create(
                    website=payment.website,
                    writer=payment.writer,
                    order=payment.order,
                    special_order=payment.special_order,
                    amount=-payment.amount,
                    bonuses=Decimal('0.00'),
                    tips=Decimal('0.00'),
                    fines=Decimal('0.00'),
                    status='Pending',
                    transaction_reference=f"ADJ-{payment.id}"
                )
                
                # Update wallet if needed
                from wallet.models import Wallet, WalletTransaction
                wallet = Wallet.objects.get(user=payment.writer.user)
                wallet.balance -= payment.amount
                wallet.save()
                
                WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type="adjustment",
                    amount=-payment.amount,
                    description=f"Payment moved to next period: {reason}"
                )

            # Mark current payment as voided
            payment.status = 'Voided'
            payment.save()

            # Find or create next payment period
            today = timezone.now().date()
            if target_period_type == 'monthly':
                # Next month's 1st
                if today.month == 12:
                    next_date = today.replace(year=today.year + 1, month=1, day=1)
                else:
                    next_date = today.replace(month=today.month + 1, day=1)
                schedule_type = 'Monthly'
            else:
                # Next bi-weekly (14 days from today)
                next_date = today + timedelta(days=14)
                schedule_type = 'Bi-Weekly'

            # Get or create payment schedule
            schedule, created = PaymentSchedule.objects.get_or_create(
                website=payment.website,
                scheduled_date=next_date,
                schedule_type=schedule_type,
                defaults={
                    'reference_code': f"{schedule_type[:2]}-{next_date.strftime('%Y%m%d')}",
                    'completed': False
                }
            )

            # Create new payment entry for next period
            new_payment = WriterPayment.objects.create(
                website=payment.website,
                writer=payment.writer,
                order=payment.order,
                special_order=payment.special_order,
                amount=payment.amount,
                bonuses=payment.bonuses,
                tips=payment.tips,
                fines=payment.fines,
                status='Pending',
                transaction_reference=f"MOVED-{payment.id}"
            )

            # Store reason in adjustment for reference
            adjustment.reason = f"Moved to next period ({schedule.reference_code}): {reason}"
            adjustment.save()

        return Response({
            'message': 'Payment moved to next period successfully',
            'new_payment_id': new_payment.id,
            'schedule_reference': schedule.reference_code,
            'reason': reason
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='adjust-for-order-status')
    def adjust_for_order_status(self, request, pk=None):
        """
        Adjust payment when order is disputed, cancelled, or revision requested.
        Automatically handles moving to next period or creating negative adjustment.
        
        Body:
        - order_status: str (required) - 'disputed', 'cancelled', 'revision_requested'
        - reason: str (optional) - Additional reason
        """
        try:
            payment = WriterPayment.objects.get(pk=pk)
        except WriterPayment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        order_status = request.data.get('order_status', '').lower()
        reason = request.data.get('reason', '')

        if order_status not in ['disputed', 'cancelled', 'revision_requested']:
            return Response(
                {'error': 'Invalid order status. Must be: disputed, cancelled, or revision_requested'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            if payment.status == 'Paid':
                # Already paid - create negative adjustment
                adjustment_amount = -payment.amount
                adjustment_reason = f"Order {order_status}: {reason}" if reason else f"Order {order_status}"
                
                WriterPaymentAdjustment.objects.create(
                    website=payment.website,
                    writer_payment=payment,
                    admin=request.user,
                    adjustment_amount=adjustment_amount,
                    reason=adjustment_reason
                )

                # Update wallet
                from wallet.models import Wallet, WalletTransaction
                wallet = Wallet.objects.get(user=payment.writer.user)
                wallet.balance += adjustment_amount
                wallet.save()
                
                WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type="adjustment",
                    amount=adjustment_amount,
                    description=adjustment_reason
                )

                # Move to next period (default to bi-weekly)
                today = timezone.now().date()
                next_date = today + timedelta(days=14)
                schedule_type = 'Bi-Weekly'

                schedule, _ = PaymentSchedule.objects.get_or_create(
                    website=payment.website,
                    scheduled_date=next_date,
                    schedule_type=schedule_type,
                    defaults={
                        'reference_code': f"{schedule_type[:2]}-{next_date.strftime('%Y%m%d')}",
                        'completed': False
                    }
                )

                # Create new payment for next period
                new_payment = WriterPayment.objects.create(
                    website=payment.website,
                    writer=payment.writer,
                    order=payment.order,
                    special_order=payment.special_order,
                    amount=payment.amount,
                    bonuses=payment.bonuses,
                    tips=payment.tips,
                    fines=payment.fines,
                    status='Pending',
                    transaction_reference=f"ADJ-{payment.id}"
                )

                payment.status = 'Voided'
                payment.save()

                return Response({
                    'message': f'Payment adjusted for {order_status}. Negative adjustment created and payment moved to next period.',
                    'adjustment_amount': str(adjustment_amount),
                    'new_payment_id': new_payment.id,
                    'schedule_reference': schedule.reference_code
                }, status=status.HTTP_200_OK)
            else:
                # Not yet paid - just update status
                if order_status == 'cancelled':
                    payment.status = 'Blocked'
                    payment.amount = Decimal('0.00')
                elif order_status in ['disputed', 'revision_requested']:
                    payment.status = 'Delayed'
                
                payment.save()

                return Response({
                    'message': f'Payment status updated to {payment.status}',
                    'payment_id': payment.id,
                    'status': payment.status
                }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='clear-payments')
    def clear_payments(self, request):
        """
        Clear payments for individual writer or all writers.
        
        Body:
        - writer_id: int (optional) - If provided, clear only this writer's payments
        - payment_ids: list (optional) - Specific payment IDs to clear
        - mark_as_paid: bool (default: True) - Mark as paid or delete
        """
        writer_id = request.data.get('writer_id')
        payment_ids = request.data.get('payment_ids', [])
        mark_as_paid = request.data.get('mark_as_paid', True)

        with transaction.atomic():
            if payment_ids:
                payments = WriterPayment.objects.filter(id__in=payment_ids, status='Pending')
            elif writer_id:
                payments = WriterPayment.objects.filter(writer_id=writer_id, status='Pending')
            else:
                payments = WriterPayment.objects.filter(status='Pending')

            cleared_count = 0
            for payment in payments:
                if mark_as_paid:
                    payment.mark_as_paid(request.user)
                else:
                    payment.delete()
                cleared_count += 1

        return Response({
            'message': f'Cleared {cleared_count} payment(s)',
            'cleared_count': cleared_count
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='payout-requests')
    def payout_requests(self, request):
        """
        Get all payout requests with filters.
        """
        status_filter = request.query_params.get('status', '')
        website_id = request.query_params.get('website_id', '')

        requests = WriterPayoutRequest.objects.all()
        
        if status_filter:
            requests = requests.filter(status=status_filter)
        if website_id:
            requests = requests.filter(website_id=website_id)

        requests = requests.select_related('writer__user', 'website').order_by('-requested_at')

        data = [{
            'id': req.id,
            'writer': {
                'id': req.writer.id,
                'name': req.writer.user.get_full_name() or req.writer.user.username,
                'email': req.writer.user.email
            },
            'website': req.website.name,
            'amount_requested': str(req.amount_requested),
            'status': req.status,
            'requested_at': req.requested_at,
            'processed_at': req.processed_at
        } for req in requests]

        return Response({'results': data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='approve-payout')
    def approve_payout(self, request, pk=None):
        """
        Approve a payout request.
        """
        try:
            payout_request = WriterPayoutRequest.objects.get(pk=pk)
        except WriterPayoutRequest.DoesNotExist:
            return Response(
                {'error': 'Payout request not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        payout_request.approve_payout(request.user)
        
        return Response({
            'message': 'Payout approved successfully',
            'payout_id': payout_request.id
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='adjustments')
    def adjustments(self, request):
        """
        Get payment adjustments with reasons.
        """
        payment_id = request.query_params.get('payment_id')
        writer_id = request.query_params.get('writer_id')

        adjustments = WriterPaymentAdjustment.objects.all()
        
        if payment_id:
            adjustments = adjustments.filter(writer_payment_id=payment_id)
        if writer_id:
            adjustments = adjustments.filter(writer_payment__writer_id=writer_id)

        adjustments = adjustments.select_related('writer_payment', 'admin', 'website').order_by('-created_at')

        data = [{
            'id': adj.id,
            'payment_id': adj.writer_payment.id,
            'writer': {
                'id': adj.writer_payment.writer.id,
                'name': adj.writer_payment.writer.user.get_full_name() or adj.writer_payment.writer.user.username
            },
            'admin': adj.admin.username,
            'adjustment_amount': str(adj.adjustment_amount),
            'reason': adj.reason,
            'created_at': adj.created_at
        } for adj in adjustments]

        return Response({'results': data}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='adjust-amount')
    def adjust_payment_amount(self, request, pk=None):
        """
        Admin adjusts the payment amount for a writer payment.
        Can adjust payments whether they were set automatically (level-based) or by admin.
        
        Request body:
        {
            "adjustment_amount": 25.00,  // Positive to increase, negative to decrease
            "reason": "Additional pages added"  // Required reason
        }
        """
        from decimal import Decimal
        from django.db import transaction
        from wallet.models import Wallet, WalletTransaction
        
        try:
            payment = WriterPayment.objects.get(pk=pk)
        except WriterPayment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        adjustment_amount = request.data.get('adjustment_amount')
        reason = request.data.get('reason', '')
        
        if adjustment_amount is None:
            return Response(
                {'error': 'adjustment_amount is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not reason:
            return Response(
                {'error': 'reason is required for adjustments'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            adjustment_amount = Decimal(str(adjustment_amount))
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid adjustment_amount format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Create adjustment record
            adjustment = WriterPaymentAdjustment.objects.create(
                website=payment.website,
                writer_payment=payment,
                admin=request.user,
                adjustment_amount=adjustment_amount,
                reason=reason
            )
            
            # Apply the adjustment
            old_amount = payment.amount
            payment.amount += adjustment_amount
            payment.amount = max(payment.amount, Decimal('0.00'))  # Ensure non-negative
            payment.save()
            
            # Update wallet if payment was already processed
            if payment.status == 'Paid':
                wallet, created = Wallet.objects.get_or_create(
                    user=payment.writer.user
                )
                wallet.balance += adjustment_amount
                wallet.save()
                
                # Log transaction
                WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type="adjustment",
                    amount=adjustment_amount,
                    description=f"Admin payment adjustment: {reason}"
                )
            
            return Response({
                'message': 'Payment amount adjusted successfully',
                'payment_id': payment.id,
                'old_amount': str(old_amount),
                'new_amount': str(payment.amount),
                'adjustment_amount': str(adjustment_amount),
                'adjustment_id': adjustment.id
            }, status=status.HTTP_200_OK)
