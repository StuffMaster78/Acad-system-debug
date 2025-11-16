from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from decimal import Decimal
from .models import (
    WriterWallet, WalletTransaction,
    WriterPaymentBatch, PaymentSchedule,
    ScheduledWriterPayment, PaymentOrderRecord,
    WriterPayment, AdminPaymentAdjustment,
    PaymentConfirmation
)
from .serializers import (
    WriterWalletSerializer, WalletTransactionSerializer,
    WriterPaymentBatchSerializer, PaymentScheduleSerializer,
    ScheduledWriterPaymentSerializer, PaymentOrderRecordSerializer,
    WriterPaymentSerializer, AdminPaymentAdjustmentSerializer,
    PaymentConfirmationSerializer
)


class WriterWalletViewSet(viewsets.ModelViewSet):
    """ API endpoint for managing writer wallets. """
    queryset = WriterWallet.objects.all()
    serializer_class = WriterWalletSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=["get"])
    def transactions(self, request, pk=None):
        """ Retrieve all transactions for a specific writer wallet. """
        wallet = self.get_object()
        transactions = WalletTransaction.objects.filter(writer_wallet=wallet)
        serializer = WalletTransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"])
    def adjust(self, request, pk=None):
        """Admin adjustment: credit or debit writer wallet"""
        wallet = self.get_object()
        amount = request.data.get('amount')
        reason = request.data.get('reason', '')
        transaction_type = request.data.get('transaction_type', 'Adjustment')
        
        if not amount:
            return Response(
                {"detail": "Amount is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = Decimal(str(amount))
        except (ValueError, TypeError):
            return Response(
                {"detail": "Invalid amount format."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not reason:
            return Response(
                {"detail": "Reason is required for adjustments."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                if amount > 0:
                    # Credit
                    wallet.balance += amount
                    wallet.total_adjustments += amount
                    wallet.save()
                    
                    # Create transaction record
                    WalletTransaction.objects.create(
                        writer_wallet=wallet,
                        website=wallet.website,
                        transaction_type=transaction_type if transaction_type != 'Adjustment' else 'Adjustment',
                        amount=amount
                    )
                    
                    message = f'Successfully credited ${amount:,.2f} to {wallet.writer.get_full_name() or wallet.writer.username}\'s wallet.'
                else:
                    # Debit (make amount positive)
                    debit_amount = abs(amount)
                    if wallet.balance < debit_amount:
                        return Response(
                            {"detail": f"Insufficient balance. Current balance: ${wallet.balance:,.2f}"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    wallet.balance -= debit_amount
                    wallet.total_adjustments += amount  # Negative adjustment
                    wallet.save()
                    
                    # Create transaction record
                    WalletTransaction.objects.create(
                        writer_wallet=wallet,
                        website=wallet.website,
                        transaction_type=transaction_type if transaction_type != 'Adjustment' else 'Fine',
                        amount=debit_amount
                    )
                    
                    message = f'Successfully debited ${debit_amount:,.2f} from {wallet.writer.get_full_name() or wallet.writer.username}\'s wallet.'
                
                # Refresh wallet
                wallet.refresh_from_db()
                serializer = WriterWalletSerializer(wallet)
                
                return Response({
                    'detail': message,
                    'wallet': serializer.data
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {"detail": f"Error adjusting wallet: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WalletTransactionViewSet(viewsets.ModelViewSet):
    """ API endpoint for wallet transactions. """
    queryset = WalletTransaction.objects.all()
    serializer_class = WalletTransactionSerializer
    permission_classes = [permissions.IsAdminUser]


class WriterPaymentBatchViewSet(viewsets.ModelViewSet):
    """ API endpoint for managing payment batches. """
    queryset = WriterPaymentBatch.objects.all()
    serializer_class = WriterPaymentBatchSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=["get"])
    def payments(self, request, pk=None):
        """ Retrieve all payments in a specific batch. """
        batch = self.get_object()
        payments = WriterPayment.objects.filter(batch=batch)
        serializer = WriterPaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentScheduleViewSet(viewsets.ModelViewSet):
    """ API endpoint for payment schedules. """
    queryset = PaymentSchedule.objects.all()
    serializer_class = PaymentScheduleSerializer
    permission_classes = [permissions.IsAdminUser]


class ScheduledWriterPaymentViewSet(viewsets.ModelViewSet):
    """ API endpoint for scheduled writer payments. """
    queryset = ScheduledWriterPayment.objects.all()
    serializer_class = ScheduledWriterPaymentSerializer
    permission_classes = [permissions.IsAdminUser]


class PaymentOrderRecordViewSet(viewsets.ModelViewSet):
    """ API endpoint for order records related to writer payments. """
    queryset = PaymentOrderRecord.objects.all()
    serializer_class = PaymentOrderRecordSerializer
    permission_classes = [permissions.IsAdminUser]


class ScheduledWriterPaymentViewSet(viewsets.ModelViewSet):
    """ API endpoint for scheduled writer payments. """
    queryset = ScheduledWriterPayment.objects.all()
    serializer_class = ScheduledWriterPaymentSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        """
        Allow admin, superadmin, and support to mark payments as paid.
        """
        if self.action in ['mark_as_paid', 'bulk_mark_as_paid']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    @action(detail=True, methods=['post'], url_path='mark-as-paid')
    def mark_as_paid(self, request, pk=None):
        """
        Mark a specific payment as paid (admin/superadmin/support only).
        """
        from django.utils.timezone import now
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Check permissions
        user = request.user
        if user.role not in ['admin', 'superadmin', 'support']:
            return Response(
                {"error": "Only admin, superadmin, and support can mark payments as paid."},
                status=403
            )
        
        try:
            payment = ScheduledWriterPayment.objects.get(pk=pk)
        except ScheduledWriterPayment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=404)
        
        if payment.status == 'Paid':
            return Response(
                {"message": "Payment is already marked as paid."},
                status=200
            )
        
        # Mark as paid
        payment.status = 'Paid'
        payment.payment_date = now()
        payment.save()
        
        # Create payment confirmation if it doesn't exist
        try:
            from .models import PaymentConfirmation
            confirmation, created = PaymentConfirmation.objects.get_or_create(
                payment=payment,
                defaults={
                    'website': payment.website,
                    'writer_wallet': payment.writer_wallet,
                    'confirmed': True,
                }
            )
            if not created:
                confirmation.confirmed = True
                confirmation.save()
        except Exception as e:
            # PaymentConfirmation might be linked to WriterPayment, not ScheduledWriterPayment
            pass
        
        return Response({
            "message": "Payment marked as paid successfully.",
            "payment": ScheduledWriterPaymentSerializer(payment).data
        }, status=200)

    @action(detail=False, methods=['post'], url_path='bulk-mark-as-paid')
    def bulk_mark_as_paid(self, request):
        """
        Mark multiple payments as paid (admin/superadmin/support only).
        Can mark all payments in a batch/period or specific payment IDs.
        """
        from django.utils.timezone import now
        from django.contrib.auth import get_user_model
        from django.db import transaction
        User = get_user_model()
        
        # Check permissions
        user = request.user
        if user.role not in ['admin', 'superadmin', 'support']:
            return Response(
                {"error": "Only admin, superadmin, and support can mark payments as paid."},
                status=403
            )
        
        payment_ids = request.data.get('payment_ids', [])
        batch_id = request.data.get('batch_id')  # PaymentSchedule ID
        schedule_id = request.data.get('schedule_id')  # PaymentSchedule ID (alias)
        writer_id = request.data.get('writer_id')  # Filter by writer
        
        if not payment_ids and not batch_id and not schedule_id:
            return Response(
                {"error": "Either payment_ids, batch_id, or schedule_id must be provided."},
                status=400
            )
        
        # Build queryset
        queryset = ScheduledWriterPayment.objects.filter(status='Pending')
        
        if payment_ids:
            queryset = queryset.filter(id__in=payment_ids)
        elif batch_id or schedule_id:
            batch_id = batch_id or schedule_id
            from .models import PaymentSchedule
            try:
                schedule = PaymentSchedule.objects.get(pk=batch_id)
                queryset = queryset.filter(batch=schedule)
            except PaymentSchedule.DoesNotExist:
                return Response({"error": "Payment schedule not found"}, status=404)
        
        if writer_id:
            queryset = queryset.filter(writer_wallet__writer_id=writer_id)
        
        # Mark all as paid
        updated_count = 0
        with transaction.atomic():
            payments = list(queryset)
            for payment in payments:
                payment.status = 'Paid'
                payment.payment_date = now()
                payment.save()
                updated_count += 1
        
        return Response({
            "message": f"Successfully marked {updated_count} payment(s) as paid.",
            "count": updated_count
        }, status=200)

    @action(detail=True, methods=['get'], url_path='breakdown')
    def payment_breakdown(self, request, pk=None):
        """
        Get detailed breakdown of a specific payment including all orders, tips, and fines.
        """
        from orders.models import Order
        from writer_management.models.tipping import Tip
        from datetime import timedelta
        
        try:
            payment = ScheduledWriterPayment.objects.select_related(
                'writer_wallet__writer__user',
                'batch',
                'website'
            ).prefetch_related('orders__order').get(pk=pk)
        except ScheduledWriterPayment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=404)
        
        # Get order details
        order_records = payment.orders.all()
        orders_data = []
        for record in order_records:
            order = record.order
            orders_data.append({
                'id': order.id,
                'topic': order.topic,
                'status': order.status,
                'amount_paid': float(record.amount_paid),
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'completed_at': order.completed_at.isoformat() if order.completed_at else None,
            })
        
        # Get tips for this payment period
        writer_user = payment.writer_wallet.writer.user
        schedule = payment.batch
        period_start = schedule.scheduled_date
        period_end = schedule.scheduled_date + timedelta(days=14 if schedule.schedule_type == 'Bi-Weekly' else 30)
        
        tips = Tip.objects.filter(
            writer=writer_user,
            website=payment.website,
            sent_at__gte=period_start,
            sent_at__lt=period_end
        ).select_related('order', 'client')
        
        tips_data = []
        for tip in tips:
            tips_data.append({
                'id': tip.id,
                'amount': float(tip.writer_earning),
                'order_id': tip.order_id,
                'order_topic': tip.order.topic if tip.order else None,
                'reason': tip.tip_reason,
                'sent_at': tip.sent_at.isoformat() if tip.sent_at else None,
            })
        
        # Get fines
        fines_data = []
        try:
            from fines.models import Fine
            fines = Fine.objects.filter(
                writer=payment.writer_wallet.writer,
                website=payment.website,
                created_at__gte=period_start,
                created_at__lt=period_end
            )
            for fine in fines:
                fines_data.append({
                    'id': fine.id,
                    'amount': float(fine.amount),
                    'reason': fine.reason,
                    'fine_type': fine.fine_type,
                    'created_at': fine.created_at.isoformat() if fine.created_at else None,
                })
        except Exception:
            pass
        
        return Response({
            'payment_id': payment.id,
            'reference_code': payment.reference_code,
            'writer': {
                'id': payment.writer_wallet.writer.id,
                'username': payment.writer_wallet.writer.user.username,
                'email': payment.writer_wallet.writer.user.email,
                'full_name': payment.writer_wallet.writer.user.get_full_name() or payment.writer_wallet.writer.user.username,
                'registration_id': payment.writer_wallet.writer.registration_id,
            },
            'amount': float(payment.amount),
            'status': payment.status,
            'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
            'period': {
                'type': schedule.schedule_type,
                'start': period_start.isoformat() if period_start else None,
                'end': period_end.isoformat() if period_end else None,
            },
            'orders': orders_data,
            'tips': tips_data,
            'fines': fines_data,
            'summary': {
                'total_orders': len(orders_data),
                'total_order_amount': float(payment.amount),
                'total_tips': sum(t['amount'] for t in tips_data),
                'total_fines': sum(f['amount'] for f in fines_data),
                'net_earnings': float(payment.amount) + sum(t['amount'] for t in tips_data) - sum(f['amount'] for f in fines_data),
            }
        })


class WriterPaymentViewSet(viewsets.ModelViewSet):
    """ API endpoint for writer payments. """
    queryset = WriterPayment.objects.all()
    serializer_class = WriterPaymentSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['get'], url_path='grouped')
    def grouped(self, request):
        """
        Get writer payments grouped by bi-weekly and monthly periods.
        
        Query params:
        - website_id: Filter by website
        - writer_id: Filter by specific writer
        - period_type: 'biweekly' or 'monthly' (default: both)
        - date_from: Start date filter
        - date_to: End date filter
        """
        from django.db.models import Sum, Count
        from django.utils import timezone
        from datetime import timedelta
        from calendar import monthrange
        
        website_id = request.query_params.get('website_id')
        writer_id = request.query_params.get('writer_id')
        period_type = request.query_params.get('period_type', 'both')  # 'biweekly', 'monthly', or 'both'
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Get payments from PaymentSchedule (bi-weekly and monthly)
        schedules = PaymentSchedule.objects.all()
        
        if website_id:
            schedules = schedules.filter(website_id=website_id)
        if date_from:
            schedules = schedules.filter(scheduled_date__gte=date_from)
        if date_to:
            schedules = schedules.filter(scheduled_date__lte=date_to)
        
        # Filter by period type
        if period_type == 'biweekly':
            schedules = schedules.filter(schedule_type='Bi-Weekly')
        elif period_type == 'monthly':
            schedules = schedules.filter(schedule_type='Monthly')
        
        # Group by period
        grouped_payments = {
            'biweekly': [],
            'monthly': [],
            'summary': {
                'total_biweekly_amount': Decimal('0.00'),
                'total_monthly_amount': Decimal('0.00'),
                'total_biweekly_payments': 0,
                'total_monthly_payments': 0,
            }
        }
        
        for schedule in schedules.select_related('website', 'processed_by').prefetch_related('payments__writer_wallet__writer'):
            scheduled_payments = ScheduledWriterPayment.objects.filter(batch=schedule)
            
            if writer_id:
                scheduled_payments = scheduled_payments.filter(writer_wallet__writer_id=writer_id)
            
            payments_data = []
            total_amount = Decimal('0.00')
            writer_count = 0
            
            for payment in scheduled_payments.select_related('writer_wallet__writer', 'writer_wallet__website').prefetch_related('orders__order'):
                # Get order count and order details
                order_records = payment.orders.all()
                order_count = order_records.count()
                order_ids = [record.order_id for record in order_records]
                
                # Calculate tips for this payment period
                writer_user = payment.writer_wallet.writer.user
                tips_total = Decimal('0.00')
                try:
                    from writer_management.models.tipping import Tip
                    # Get tips within the payment period
                    period_start = schedule.scheduled_date
                    period_end = schedule.scheduled_date + timedelta(days=14 if schedule.schedule_type == 'Bi-Weekly' else 30)
                    tips = Tip.objects.filter(
                        writer=writer_user,
                        website=schedule.website,
                        sent_at__gte=period_start,
                        sent_at__lt=period_end
                    )
                    tips_total = sum(tip.writer_earning for tip in tips)
                except Exception:
                    pass
                
                # Calculate fines for this payment period
                fines_total = Decimal('0.00')
                try:
                    from fines.models import Fine
                    fines = Fine.objects.filter(
                        writer=payment.writer_wallet.writer,
                        website=schedule.website,
                        created_at__gte=period_start,
                        created_at__lt=period_end,
                        status__in=['active', 'paid']
                    )
                    fines_total = sum(fine.amount for fine in fines)
                except Exception:
                    # Fallback to wallet transactions
                    try:
                        from writer_wallet.models import WalletTransaction
                        fines_transactions = WalletTransaction.objects.filter(
                            writer_wallet=payment.writer_wallet,
                            transaction_type='Fine',
                            created_at__gte=period_start,
                            created_at__lt=period_end
                        )
                        fines_total = sum(abs(t.amount) for t in fines_transactions)
                    except Exception:
                        pass
                
                # Calculate total earnings (amount + tips - fines)
                total_earnings = payment.amount + tips_total - fines_total
                
                payments_data.append({
                    'id': payment.id,
                    'writer': {
                        'id': payment.writer_wallet.writer.id,
                        'username': payment.writer_wallet.writer.user.username,
                        'email': payment.writer_wallet.writer.user.email,
                        'full_name': payment.writer_wallet.writer.user.get_full_name() or payment.writer_wallet.writer.user.username,
                        'registration_id': payment.writer_wallet.writer.registration_id,
                    },
                    'amount': float(payment.amount),
                    'tips': float(tips_total),
                    'fines': float(fines_total),
                    'total_earnings': float(total_earnings),
                    'order_count': order_count,
                    'order_ids': order_ids,
                    'status': payment.status,
                    'reference_code': payment.reference_code,
                    'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
                })
                total_amount += payment.amount
                writer_count += 1
            
            # Calculate totals for this period
            total_tips = sum(Decimal(str(p.get('tips', 0))) for p in payments_data)
            total_fines = sum(Decimal(str(p.get('fines', 0))) for p in payments_data)
            total_earnings = sum(Decimal(str(p.get('total_earnings', 0))) for p in payments_data)
            total_orders = sum(p.get('order_count', 0) for p in payments_data)
            
            period_data = {
                'schedule_id': schedule.id,
                'reference_code': schedule.reference_code,
                'schedule_type': schedule.schedule_type,
                'scheduled_date': schedule.scheduled_date.isoformat() if schedule.scheduled_date else None,
                'completed': schedule.completed,
                'processed_by': {
                    'id': schedule.processed_by.id,
                    'username': schedule.processed_by.username,
                } if schedule.processed_by else None,
                'website': {
                    'id': schedule.website.id,
                    'name': schedule.website.name,
                    'domain': schedule.website.domain,
                },
                'total_amount': float(total_amount),
                'total_tips': float(total_tips),
                'total_fines': float(total_fines),
                'total_earnings': float(total_earnings),
                'total_orders': total_orders,
                'writer_count': writer_count,
                'payments': payments_data,
            }
            
            if schedule.schedule_type == 'Bi-Weekly':
                grouped_payments['biweekly'].append(period_data)
                grouped_payments['summary']['total_biweekly_amount'] += total_amount
                grouped_payments['summary']['total_biweekly_payments'] += writer_count
            else:
                grouped_payments['monthly'].append(period_data)
                grouped_payments['summary']['total_monthly_amount'] += total_amount
                grouped_payments['summary']['total_monthly_payments'] += writer_count
        
        # Convert summary to float for JSON serialization
        grouped_payments['summary']['total_biweekly_amount'] = float(grouped_payments['summary']['total_biweekly_amount'])
        grouped_payments['summary']['total_monthly_amount'] = float(grouped_payments['summary']['total_monthly_amount'])
        
        # Sort by scheduled_date descending
        grouped_payments['biweekly'].sort(key=lambda x: x['scheduled_date'], reverse=True)
        grouped_payments['monthly'].sort(key=lambda x: x['scheduled_date'], reverse=True)
        
        return Response(grouped_payments, status=status.HTTP_200_OK)


class AdminPaymentAdjustmentViewSet(viewsets.ModelViewSet):
    """ API endpoint for admin adjustments to writer payments. """
    queryset = AdminPaymentAdjustment.objects.all()
    serializer_class = AdminPaymentAdjustmentSerializer
    permission_classes = [permissions.IsAdminUser]


class PaymentConfirmationViewSet(viewsets.ModelViewSet):
    """ API endpoint for confirming payments. """
    queryset = PaymentConfirmation.objects.all()
    serializer_class = PaymentConfirmationSerializer
    permission_classes = [permissions.IsAdminUser]
