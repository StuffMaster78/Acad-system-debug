"""
Views for order payment management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum, Count
from django.db import models
from django.utils import timezone
from datetime import timedelta
import logging

from .models import OrderPayment, FailedPayment
from .serializers import TransactionSerializer
from .services.payment_service import OrderPaymentService
from .services.receipt_service import ReceiptService
from orders.models import Order
from authentication.permissions import IsSuperadminOrAdmin
from rest_framework.permissions import IsAuthenticated
from client_wallet.models import ClientWalletTransaction
from writer_wallet.models import WalletTransaction
from writer_management.models.tipping import Tip
from special_orders.models import WriterBonus

logger = logging.getLogger(__name__)

class OrderPaymentViewSet(viewsets.ModelViewSet):
    """
    Viewset for handling order payments, including refunds.
    Supports all payment types: standard orders, special orders, installments, classes, wallet loading.

    Notes on permissions:
    - Admin/Superadmin: full access to all actions.
    - Authenticated clients: read-only access to their own payments via the
      ``client_payments`` and ``download_receipt`` actions.
    """
    queryset = OrderPayment.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]

    def get_permissions(self):
        """
        Relax permissions for client-facing read-only actions while keeping
        admin-only protection for management actions.
        """
        if self.action in ["client_payments", "download_receipt"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsSuperadminOrAdmin()]
    http_method_names = ["get", "post", "patch", "delete"]  # Limit methods if needed

    def get_queryset(self):
        """
        Filter payments based on payment_type and user role.
        
        Query params:
        - payment_type: Filter by payment type (standard, predefined_special, etc.)
        - order_id: Filter by order ID (for standard payments)
        - special_order_id: Filter by special order ID
        - class_purchase_id: Filter by class purchase ID
        - installment_id: Filter by installment ID (via related_object_id)
        """
        queryset = OrderPayment.objects.all()
        
        # Non-staff users only see their own payments
        if not self.request.user.is_staff:
            queryset = queryset.filter(client=self.request.user)
        
        # Filter by payment type
        payment_type = self.request.query_params.get('payment_type')
        if payment_type:
            queryset = queryset.filter(payment_type=payment_type)
        
        # Filter by order relationships
        order_id = self.request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(order_id=order_id, payment_type='standard')
        
        special_order_id = self.request.query_params.get('special_order_id')
        if special_order_id:
            queryset = queryset.filter(
                special_order_id=special_order_id,
                payment_type__in=['predefined_special', 'estimated_special', 'special_installment']
            )
        
        class_purchase_id = self.request.query_params.get('class_purchase_id')
        if class_purchase_id:
            queryset = queryset.filter(class_purchase_id=class_purchase_id, payment_type='class_payment')
        
        installment_id = self.request.query_params.get('installment_id')
        if installment_id:
            queryset = queryset.filter(
                related_object_id=installment_id,
                related_object_type='installment_payment',
                payment_type='special_installment'
            )
        
        return queryset.select_related('order', 'special_order', 'class_purchase', 'client', 'website')

    @action(detail=False, methods=['get'], url_path='all-transactions')
    def all_transactions(self, request):
        """
        Get all payment transactions including wallet transactions.
        Returns a unified list of all payments and wallet transactions.
        """
        from rest_framework.pagination import PageNumberPagination
        
        class PaymentLogPagination(PageNumberPagination):
            page_size = 50
            page_size_query_param = 'page_size'
            max_page_size = 200
        
        # Get query parameters
        website_id = request.query_params.get('website_id')
        payment_type = request.query_params.get('payment_type')
        status_filter = request.query_params.get('status')
        search = request.query_params.get('search')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Build combined transactions list
        transactions = []
        
        # Get OrderPayments
        order_payments = OrderPayment.objects.all()
        if website_id:
            order_payments = order_payments.filter(website_id=website_id)
        if payment_type:
            order_payments = order_payments.filter(payment_type=payment_type)
        if status_filter:
            order_payments = order_payments.filter(status=status_filter)
        if date_from:
            order_payments = order_payments.filter(created_at__gte=date_from)
        if date_to:
            order_payments = order_payments.filter(created_at__lte=date_to)
        if search:
            order_payments = order_payments.filter(
                Q(transaction_id__icontains=search) |
                Q(reference_id__icontains=search) |
                Q(client__email__icontains=search) |
                Q(client__username__icontains=search)
            )
        
        for payment in order_payments.select_related('client', 'website', 'order', 'special_order', 'class_purchase'):
            try:
                # Determine the payment type label
                payment_type_label = payment.get_payment_type_display() if hasattr(payment, 'get_payment_type_display') else payment.payment_type
                
                # Get related object ID based on payment type
                related_id = None
                related_type = None
                if payment.order:
                    related_id = payment.order.id
                    related_type = 'order'
                elif payment.special_order:
                    related_id = payment.special_order.id
                    related_type = 'special_order'
                elif payment.class_purchase:
                    related_id = payment.class_purchase.id
                    related_type = 'class_purchase'
                
                transactions.append({
                    'id': f'order_payment_{payment.id}',
                    'type': 'order_payment',
                    'payment_type': payment.payment_type,
                    'payment_type_label': payment_type_label,
                    'amount': float(payment.amount) if payment.amount else 0.0,
                    'status': payment.status,
                    'payment_method': payment.payment_method or 'N/A',
                    'client': {
                        'id': payment.client.id if payment.client else None,
                        'email': payment.client.email if payment.client else None,
                        'username': payment.client.username if payment.client else None
                    } if payment.client else None,
                    'website': {
                        'id': payment.website.id if payment.website else None,
                        'name': payment.website.name if payment.website else None,
                        'domain': payment.website.domain if payment.website else None
                    } if payment.website else None,
                    'order_id': payment.order.id if payment.order else None,
                    'special_order_id': payment.special_order.id if payment.special_order else None,
                    'class_purchase_id': payment.class_purchase.id if payment.class_purchase else None,
                    'related_id': related_id,
                    'related_type': related_type,
                    'reference_id': payment.reference_id,
                    'transaction_id': payment.transaction_id,
                    'created_at': payment.created_at,
                    'confirmed_at': payment.confirmed_at,
                })
            except Exception as e:
                logger.error(f"Error processing order payment {payment.id}: {e}", exc_info=True)
                continue  # Skip this payment and continue with others
        
        # Get Client Wallet Transactions (new model)
        client_wallet_transactions = ClientWalletTransaction.objects.all()
        if website_id:
            client_wallet_transactions = client_wallet_transactions.filter(wallet__website_id=website_id)
        if date_from:
            client_wallet_transactions = client_wallet_transactions.filter(created_at__gte=date_from)
        if date_to:
            client_wallet_transactions = client_wallet_transactions.filter(created_at__lte=date_to)
        if search:
            client_wallet_transactions = client_wallet_transactions.filter(
                Q(wallet__user__email__icontains=search) |
                Q(wallet__user__username__icontains=search) |
                Q(transaction_reference__icontains=search)
            )
        
        for transaction in client_wallet_transactions.select_related('wallet__user', 'wallet__website'):
            try:
                if not transaction.wallet or not transaction.wallet.user:
                    continue  # Skip transactions with missing wallet or user
                
                transactions.append({
                    'id': f'client_wallet_{transaction.id}',
                    'type': 'client_wallet',
                    'payment_type': 'wallet_transaction',
                    'payment_type_label': transaction.transaction_type.replace('_', ' ').title() if hasattr(transaction, 'transaction_type') else 'Wallet Transaction',
                    'amount': float(transaction.amount) if transaction.amount else 0.0,
                    'status': 'completed',
                    'payment_method': 'wallet',
                    'client': {
                        'id': transaction.wallet.user.id,
                        'email': transaction.wallet.user.email,
                        'username': transaction.wallet.user.username
                    },
                    'website': {
                        'id': transaction.wallet.website.id if transaction.wallet.website else None,
                        'name': transaction.wallet.website.name if transaction.wallet.website else None,
                        'domain': transaction.wallet.website.domain if transaction.wallet.website else None
                    } if transaction.wallet.website else None,
                    'order_id': None,
                    'reference_id': transaction.transaction_reference or f'wallet_{transaction.id}',
                    'transaction_id': f'wallet_{transaction.id}',
                    'created_at': transaction.created_at,
                    'confirmed_at': transaction.created_at,
                    'is_credit': transaction.is_credit if hasattr(transaction, 'is_credit') else None,
                    'source': transaction.source if hasattr(transaction, 'source') else None,
                    'description': transaction.description if hasattr(transaction, 'description') else None,
                })
            except Exception as e:
                logger.error(f"Error processing client wallet transaction {transaction.id}: {e}", exc_info=True)
                continue  # Skip this transaction and continue with others
        
        # Get Client Wallet Transactions (old model - wallet app)
        try:
            from wallet.models import WalletTransaction as OldWalletTransaction
            old_wallet_transactions = OldWalletTransaction.objects.all()
            if website_id:
                old_wallet_transactions = old_wallet_transactions.filter(website_id=website_id)
            if date_from:
                old_wallet_transactions = old_wallet_transactions.filter(created_at__gte=date_from)
            if date_to:
                old_wallet_transactions = old_wallet_transactions.filter(created_at__lte=date_to)
            if search:
                old_wallet_transactions = old_wallet_transactions.filter(
                    Q(wallet__user__email__icontains=search) |
                    Q(wallet__user__username__icontains=search)
                )
            
            for transaction in old_wallet_transactions.select_related('wallet__user', 'website'):
                transactions.append({
                    'id': f'old_wallet_{transaction.id}',
                    'type': 'client_wallet',
                    'payment_type': 'wallet_transaction',
                    'payment_type_label': transaction.transaction_type.replace('_', ' ').title() if hasattr(transaction, 'transaction_type') else 'Wallet Transaction',
                    'amount': float(transaction.amount),
                    'status': 'completed',
                    'payment_method': 'wallet',
                    'client': {
                        'id': transaction.wallet.user.id,
                        'email': transaction.wallet.user.email,
                        'username': transaction.wallet.user.username
                    },
                    'website': {
                        'id': transaction.website.id,
                        'name': transaction.website.name,
                        'domain': transaction.website.domain
                    } if transaction.website else None,
                    'order_id': None,
                    'reference_id': f'wallet_{transaction.id}',
                    'transaction_id': f'old_wallet_{transaction.id}',
                    'created_at': transaction.created_at,
                    'confirmed_at': transaction.created_at,
                    'description': transaction.description if hasattr(transaction, 'description') else None,
                })
        except Exception:
            pass  # Old model might not exist
        
        # Get Writer Wallet Transactions
        writer_wallet_transactions = WalletTransaction.objects.all()
        if website_id:
            writer_wallet_transactions = writer_wallet_transactions.filter(writer_wallet__website_id=website_id)
        if date_from:
            writer_wallet_transactions = writer_wallet_transactions.filter(created_at__gte=date_from)
        if date_to:
            writer_wallet_transactions = writer_wallet_transactions.filter(created_at__lte=date_to)
        if search:
            writer_wallet_transactions = writer_wallet_transactions.filter(
                Q(writer_wallet__writer__email__icontains=search) |
                Q(writer_wallet__writer__username__icontains=search) |
                Q(reference_code__icontains=search)
            )
        
        for transaction in writer_wallet_transactions.select_related('writer_wallet__writer', 'writer_wallet__website', 'order'):
            try:
                if not transaction.writer_wallet or not transaction.writer_wallet.writer:
                    continue  # Skip transactions with missing wallet or writer
                
                transactions.append({
                    'id': f'writer_wallet_{transaction.id}',
                    'type': 'writer_wallet',
                    'payment_type': transaction.transaction_type.lower().replace(' ', '_') if hasattr(transaction, 'transaction_type') else 'unknown',
                    'payment_type_label': transaction.transaction_type if hasattr(transaction, 'transaction_type') else 'Writer Wallet Transaction',
                    'amount': float(transaction.amount) if transaction.amount else 0.0,
                    'status': 'completed',
                    'payment_method': 'wallet',
                    'writer': {
                        'id': transaction.writer_wallet.writer.id,
                        'email': transaction.writer_wallet.writer.email,
                        'username': transaction.writer_wallet.writer.username
                    },
                    'website': {
                        'id': transaction.writer_wallet.website.id if transaction.writer_wallet.website else None,
                        'name': transaction.writer_wallet.website.name if transaction.writer_wallet.website else None,
                        'domain': transaction.writer_wallet.website.domain if transaction.writer_wallet.website else None
                    } if transaction.writer_wallet.website else None,
                    'order_id': transaction.order.id if transaction.order else None,
                    'reference_id': transaction.reference_code or f'writer_wallet_{transaction.id}',
                    'transaction_id': f'writer_wallet_{transaction.id}',
                    'created_at': transaction.created_at,
                    'confirmed_at': transaction.created_at,
                })
            except Exception as e:
                logger.error(f"Error processing writer wallet transaction {transaction.id}: {e}", exc_info=True)
                continue  # Skip this transaction and continue with others
        
        # Get Tips
        tips = Tip.objects.all()
        if website_id:
            tips = tips.filter(website_id=website_id)
        if date_from:
            tips = tips.filter(sent_at__gte=date_from) if hasattr(Tip, 'sent_at') else tips.filter(created_at__gte=date_from)
        if date_to:
            tips = tips.filter(sent_at__lte=date_to) if hasattr(Tip, 'sent_at') else tips.filter(created_at__lte=date_to)
        if search:
            tips = tips.filter(
                Q(client__email__icontains=search) |
                Q(client__username__icontains=search) |
                Q(writer__email__icontains=search) |
                Q(writer__username__icontains=search)
            )
        
        for tip in tips.select_related('client', 'writer', 'website', 'order'):
            try:
                if not tip.client or not tip.writer:
                    continue  # Skip tips with missing client or writer
                
                tip_date = tip.sent_at if hasattr(tip, 'sent_at') and tip.sent_at else (tip.created_at if hasattr(tip, 'created_at') else timezone.now())
                transactions.append({
                    'id': f'tip_{tip.id}',
                    'type': 'tip',
                    'payment_type': 'tip',
                    'payment_type_label': f'Tip ({tip.get_tip_type_display() if hasattr(tip, "get_tip_type_display") else tip.tip_type})',
                    'amount': float(tip.tip_amount) if tip.tip_amount else 0.0,
                    'status': 'completed',
                    'payment_method': 'tip',
                    'client': {
                        'id': tip.client.id,
                        'email': tip.client.email,
                        'username': tip.client.username
                    },
                    'writer': {
                        'id': tip.writer.id,
                        'email': tip.writer.email,
                        'username': tip.writer.username
                    },
                    'website': {
                        'id': tip.website.id if tip.website else None,
                        'name': tip.website.name if tip.website else None,
                        'domain': tip.website.domain if tip.website else None
                    } if tip.website else None,
                    'order_id': tip.order.id if tip.order else None,
                    'reference_id': f'tip_{tip.id}',
                    'transaction_id': f'tip_{tip.id}',
                    'created_at': tip_date,
                    'confirmed_at': tip_date,
                    'tip_reason': tip.tip_reason if hasattr(tip, 'tip_reason') else None,
                })
            except Exception as e:
                logger.error(f"Error processing tip {tip.id}: {e}", exc_info=True)
                continue  # Skip this tip and continue with others
        
        # Get Writer Bonuses
        bonuses = WriterBonus.objects.all()
        if website_id:
            bonuses = bonuses.filter(website_id=website_id)
        if date_from:
            bonuses = bonuses.filter(granted_at__gte=date_from)
        if date_to:
            bonuses = bonuses.filter(granted_at__lte=date_to)
        if search:
            bonuses = bonuses.filter(
                Q(writer__email__icontains=search) |
                Q(writer__username__icontains=search)
            )
        
        for bonus in bonuses.select_related('writer', 'website', 'special_order'):
            try:
                if not bonus.writer:
                    continue  # Skip bonuses with missing writer
                
                transactions.append({
                    'id': f'bonus_{bonus.id}',
                    'type': 'bonus',
                    'payment_type': 'bonus',
                    'payment_type_label': f'Bonus ({bonus.get_category_display() if hasattr(bonus, "get_category_display") else bonus.category})',
                    'amount': float(bonus.amount) if bonus.amount else 0.0,
                    'status': 'completed' if bonus.is_paid else 'pending',
                    'payment_method': 'bonus',
                    'writer': {
                        'id': bonus.writer.id,
                        'email': bonus.writer.email,
                        'username': bonus.writer.username
                    },
                    'website': {
                        'id': bonus.website.id if bonus.website else None,
                        'name': bonus.website.name if bonus.website else None,
                        'domain': bonus.website.domain if bonus.website else None
                    } if bonus.website else None,
                    'special_order_id': bonus.special_order.id if bonus.special_order else None,
                    'reference_id': f'bonus_{bonus.id}',
                    'transaction_id': f'bonus_{bonus.id}',
                    'created_at': bonus.granted_at,
                    'confirmed_at': bonus.granted_at if bonus.is_paid else None,
                    'bonus_reason': bonus.reason if hasattr(bonus, 'reason') else None,
                })
            except Exception as e:
                logger.error(f"Error processing bonus {bonus.id}: {e}", exc_info=True)
                continue  # Skip this bonus and continue with others
        
        # Sort by created_at descending (handle None values)
        transactions.sort(key=lambda x: x.get('created_at') or timezone.now(), reverse=True)
        
        # Paginate
        paginator = PaymentLogPagination()
        page = paginator.paginate_queryset(transactions, request)
        
        if page is not None:
            return paginator.get_paginated_response(page)
        
        return Response({
            'results': transactions,
            'count': len(transactions),
            'next': None,
            'previous': None
        })
    
    @action(detail=False, methods=['get'], url_path='client-payments')
    def client_payments(self, request):
        """
        Get all client payment transactions only (excludes writer transactions).
        Returns order payments, client wallet transactions, tips given, and wallet top-ups.
        """
        from rest_framework.pagination import PageNumberPagination
        
        class ClientPaymentPagination(PageNumberPagination):
            page_size = 50
            page_size_query_param = 'page_size'
            max_page_size = 200
        
        # Get query parameters
        website_id = request.query_params.get('website_id')
        payment_type = request.query_params.get('payment_type')
        status_filter = request.query_params.get('status')
        search = request.query_params.get('search')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        # For non-staff users, always scope to the authenticated client.
        # Admins can optionally filter by client_id.
        if request.user.is_staff:
            client_id = request.query_params.get('client_id')
        else:
            client_id = request.user.id
        
        # Build combined transactions list (CLIENT PAYMENTS ONLY)
        transactions = []
        
        # Get OrderPayments (all client payments)
        order_payments = OrderPayment.objects.all()
        if website_id:
            order_payments = order_payments.filter(website_id=website_id)
        if client_id:
            order_payments = order_payments.filter(client_id=client_id)
        if payment_type:
            order_payments = order_payments.filter(payment_type=payment_type)
        if status_filter:
            order_payments = order_payments.filter(status=status_filter)
        if date_from:
            order_payments = order_payments.filter(created_at__gte=date_from)
        if date_to:
            order_payments = order_payments.filter(created_at__lte=date_to)
        if search:
            order_payments = order_payments.filter(
                Q(transaction_id__icontains=search) |
                Q(reference_id__icontains=search) |
                Q(client__email__icontains=search) |
                Q(client__username__icontains=search)
            )
        
        for payment in order_payments.select_related('client', 'website', 'order', 'special_order', 'class_purchase'):
            payment_type_label = payment.get_payment_type_display() if hasattr(payment, 'get_payment_type_display') else payment.payment_type
            
            related_id = None
            related_type = None
            if payment.order:
                related_id = payment.order.id
                related_type = 'order'
            elif payment.special_order:
                related_id = payment.special_order.id
                related_type = 'special_order'
            elif payment.class_purchase:
                related_id = payment.class_purchase.id
                related_type = 'class_purchase'
            
            transactions.append({
                'id': f'order_payment_{payment.id}',
                'type': 'order_payment',
                'payment_type': payment.payment_type,
                'payment_type_label': payment_type_label,
                'amount': float(payment.amount),
                'status': payment.status,
                'payment_method': payment.payment_method or 'N/A',
                'client': {
                    'id': payment.client.id,
                    'email': payment.client.email,
                    'username': payment.client.username
                },
                'website': {
                    'id': payment.website.id,
                    'name': payment.website.name,
                    'domain': payment.website.domain
                },
                'order_id': payment.order.id if payment.order else None,
                'special_order_id': payment.special_order.id if payment.special_order else None,
                'class_purchase_id': payment.class_purchase.id if payment.class_purchase else None,
                'related_id': related_id,
                'related_type': related_type,
                'reference_id': payment.reference_id,
                'transaction_id': payment.transaction_id,
                'created_at': payment.created_at,
                'confirmed_at': payment.confirmed_at,
            })
        
        # Get Client Wallet Transactions
        client_wallet_transactions = ClientWalletTransaction.objects.all()
        if website_id:
            client_wallet_transactions = client_wallet_transactions.filter(wallet__website_id=website_id)
        if client_id:
            client_wallet_transactions = client_wallet_transactions.filter(wallet__user_id=client_id)
        if date_from:
            client_wallet_transactions = client_wallet_transactions.filter(created_at__gte=date_from)
        if date_to:
            client_wallet_transactions = client_wallet_transactions.filter(created_at__lte=date_to)
        if search:
            client_wallet_transactions = client_wallet_transactions.filter(
                Q(wallet__user__email__icontains=search) |
                Q(wallet__user__username__icontains=search) |
                Q(reference_id__icontains=search)
            )
        
        for transaction in client_wallet_transactions.select_related('wallet__user', 'wallet__website'):
            transactions.append({
                'id': f'client_wallet_{transaction.id}',
                'type': 'client_wallet',
                'payment_type': 'wallet_transaction',
                'payment_type_label': transaction.transaction_type.replace('_', ' ').title() if hasattr(transaction, 'transaction_type') else 'Wallet Transaction',
                'amount': float(transaction.amount),
                'status': 'completed',
                'payment_method': 'wallet',
                'client': {
                    'id': transaction.wallet.user.id,
                    'email': transaction.wallet.user.email,
                    'username': transaction.wallet.user.username
                },
                'website': {
                    'id': transaction.wallet.website.id,
                    'name': transaction.wallet.website.name,
                    'domain': transaction.wallet.website.domain
                } if transaction.wallet.website else None,
                'order_id': None,
                'reference_id': transaction.reference_id or f'wallet_{transaction.id}',
                'transaction_id': f'wallet_{transaction.id}',
                'created_at': transaction.created_at,
                'confirmed_at': transaction.created_at,
                'description': transaction.description if hasattr(transaction, 'description') else None,
            })
        
        # Get Tips (given by clients)
        tips = Tip.objects.all()
        if website_id:
            tips = tips.filter(website_id=website_id)
        if client_id:
            tips = tips.filter(client_id=client_id)
        if date_from:
            tips = tips.filter(sent_at__gte=date_from) if hasattr(Tip, 'sent_at') else tips.filter(created_at__gte=date_from)
        if date_to:
            tips = tips.filter(sent_at__lte=date_to) if hasattr(Tip, 'sent_at') else tips.filter(created_at__lte=date_to)
        if search:
            tips = tips.filter(
                Q(client__email__icontains=search) |
                Q(client__username__icontains=search) |
                Q(writer__email__icontains=search) |
                Q(writer__username__icontains=search)
            )
        
        for tip in tips.select_related('client', 'writer', 'website', 'order'):
            tip_date = tip.sent_at if hasattr(tip, 'sent_at') and tip.sent_at else (tip.created_at if hasattr(tip, 'created_at') else timezone.now())
            transactions.append({
                'id': f'tip_{tip.id}',
                'type': 'tip',
                'payment_type': 'tip',
                'payment_type_label': f'Tip ({tip.get_tip_type_display() if hasattr(tip, "get_tip_type_display") else tip.tip_type})',
                'amount': float(tip.tip_amount),
                'status': 'completed',
                'payment_method': 'tip',
                'client': {
                    'id': tip.client.id,
                    'email': tip.client.email,
                    'username': tip.client.username
                },
                'writer': {
                    'id': tip.writer.id,
                    'email': tip.writer.email,
                    'username': tip.writer.username
                },
                'website': {
                    'id': tip.website.id,
                    'name': tip.website.name,
                    'domain': tip.website.domain
                } if tip.website else None,
                'order_id': tip.order.id if tip.order else None,
                'reference_id': f'tip_{tip.id}',
                'transaction_id': f'tip_{tip.id}',
                'created_at': tip_date,
                'confirmed_at': tip_date,
                'tip_reason': tip.tip_reason if hasattr(tip, 'tip_reason') else None,
            })
        
        # Get Client Wallet Transactions (old model - wallet app)
        try:
            from wallet.models import WalletTransaction as OldWalletTransaction
            old_wallet_transactions = OldWalletTransaction.objects.all()
            if website_id:
                old_wallet_transactions = old_wallet_transactions.filter(website_id=website_id)
            if client_id:
                old_wallet_transactions = old_wallet_transactions.filter(wallet__user_id=client_id)
            if date_from:
                old_wallet_transactions = old_wallet_transactions.filter(created_at__gte=date_from)
            if date_to:
                old_wallet_transactions = old_wallet_transactions.filter(created_at__lte=date_to)
            if search:
                old_wallet_transactions = old_wallet_transactions.filter(
                    Q(wallet__user__email__icontains=search) |
                    Q(wallet__user__username__icontains=search)
                )
            
            for transaction in old_wallet_transactions.select_related('wallet__user', 'website'):
                transactions.append({
                    'id': f'old_wallet_{transaction.id}',
                    'type': 'client_wallet',
                    'payment_type': 'wallet_transaction',
                    'payment_type_label': transaction.transaction_type.replace('_', ' ').title() if hasattr(transaction, 'transaction_type') else 'Wallet Transaction',
                    'amount': float(transaction.amount),
                    'status': 'completed',
                    'payment_method': 'wallet',
                    'client': {
                        'id': transaction.wallet.user.id,
                        'email': transaction.wallet.user.email,
                        'username': transaction.wallet.user.username
                    },
                    'website': {
                        'id': transaction.website.id,
                        'name': transaction.website.name,
                        'domain': transaction.website.domain
                    } if transaction.website else None,
                    'order_id': None,
                    'reference_id': f'wallet_{transaction.id}',
                    'transaction_id': f'old_wallet_{transaction.id}',
                    'created_at': transaction.created_at,
                    'confirmed_at': transaction.created_at,
                    'description': transaction.description if hasattr(transaction, 'description') else None,
                })
        except Exception:
            pass  # Old model might not exist
        
        # Sort by created_at descending (handle None values)
        transactions.sort(key=lambda x: x.get('created_at') or timezone.now(), reverse=True)
        
        # Paginate
        paginator = ClientPaymentPagination()
        page = paginator.paginate_queryset(transactions, request)
        
        if page is not None:
            return paginator.get_paginated_response(page)
        
        return Response({
            'results': transactions,
            'count': len(transactions),
            'next': None,
            'previous': None
        })
    
    @action(detail=False, methods=['get'], url_path='receipt/(?P<transaction_id>[^/.]+)')
    def download_receipt(self, request, transaction_id=None):
        """
        Download a PDF receipt for a transaction.
        
        Transaction ID format:
        - order_payment_{id} - For order payments
        - client_wallet_{id} - For client wallet transactions
        - writer_wallet_{id} - For writer wallet transactions
        """
        try:
            # Parse transaction ID
            if transaction_id.startswith('order_payment_'):
                payment_id = int(transaction_id.replace('order_payment_', ''))
                payment = OrderPayment.objects.select_related('client', 'website', 'order').get(id=payment_id)
                
                # Check permissions - users can only download their own receipts unless staff
                if not request.user.is_staff and payment.client != request.user:
                    return Response(
                        {"error": "You don't have permission to download this receipt."},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                transaction_data = {
                    'id': f'order_payment_{payment.id}',
                    'type': 'order_payment',
                    'payment_type': payment.payment_type,
                    'amount': float(payment.amount),
                    'status': payment.status,
                    'payment_method': payment.payment_method or 'N/A',
                    'client': {
                        'id': payment.client.id,
                        'email': payment.client.email,
                        'username': payment.client.username
                    },
                    'website': {
                        'id': payment.website.id,
                        'name': payment.website.name,
                        'domain': payment.website.domain
                    },
                    'order_id': payment.order.id if payment.order else None,
                    'reference_id': payment.reference_id,
                    'transaction_id': payment.transaction_id,
                    'created_at': payment.created_at,
                    'confirmed_at': payment.confirmed_at,
                }
                website_name = payment.website.name if payment.website else "Writing System"
                
            elif transaction_id.startswith('client_wallet_'):
                wallet_id = int(transaction_id.replace('client_wallet_', ''))
                transaction = ClientWalletTransaction.objects.select_related('wallet__user', 'wallet__website').get(id=wallet_id)
                
                # Check permissions
                if not request.user.is_staff and transaction.wallet.user != request.user:
                    return Response(
                        {"error": "You don't have permission to download this receipt."},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                transaction_data = {
                    'id': f'client_wallet_{transaction.id}',
                    'type': 'client_wallet',
                    'payment_type': 'wallet_transaction',
                    'amount': float(transaction.amount),
                    'status': 'completed',
                    'payment_method': 'wallet',
                    'client': {
                        'id': transaction.wallet.user.id,
                        'email': transaction.wallet.user.email,
                        'username': transaction.wallet.user.username
                    },
                    'website': {
                        'id': transaction.wallet.website.id,
                        'name': transaction.wallet.website.name,
                        'domain': transaction.wallet.website.domain
                    } if transaction.wallet.website else None,
                    'order_id': None,
                    'reference_id': transaction.transaction_reference or f'wallet_{transaction.id}',
                    'transaction_id': f'wallet_{transaction.id}',
                    'created_at': transaction.created_at,
                    'confirmed_at': transaction.created_at,
                    'is_credit': transaction.is_credit,
                    'source': transaction.source,
                }
                website_name = transaction.wallet.website.name if transaction.wallet.website else "Writing System"
                
            elif transaction_id.startswith('writer_wallet_'):
                wallet_id = int(transaction_id.replace('writer_wallet_', ''))
                transaction = WalletTransaction.objects.select_related('writer_wallet__writer', 'writer_wallet__website').get(id=wallet_id)
                
                # Check permissions - writers can download their own receipts, staff can download any
                if not request.user.is_staff:
                    writer_user = getattr(transaction.writer_wallet.writer, 'user', None)
                    if not writer_user or writer_user != request.user:
                        return Response(
                            {"error": "You don't have permission to download this receipt."},
                            status=status.HTTP_403_FORBIDDEN
                        )
                
                transaction_data = {
                    'id': f'writer_wallet_{transaction.id}',
                    'type': 'writer_wallet',
                    'payment_type': transaction.transaction_type,
                    'amount': float(transaction.amount),
                    'status': 'completed',
                    'payment_method': 'wallet',
                    'writer': {
                        'id': transaction.writer_wallet.writer.id,
                        'email': getattr(transaction.writer_wallet.writer, 'email', 'N/A'),
                        'username': getattr(transaction.writer_wallet.writer, 'username', 'N/A')
                    },
                    'website': {
                        'id': transaction.writer_wallet.website.id,
                        'name': transaction.writer_wallet.website.name,
                        'domain': transaction.writer_wallet.website.domain
                    } if transaction.writer_wallet.website else None,
                    'order_id': None,
                    'reference_id': transaction.reference_code or f'writer_wallet_{transaction.id}',
                    'transaction_id': f'writer_wallet_{transaction.id}',
                    'created_at': transaction.created_at,
                    'confirmed_at': transaction.created_at,
                }
                website_name = transaction.writer_wallet.website.name if transaction.writer_wallet.website else "Writing System"
                
            else:
                return Response(
                    {"error": "Invalid transaction ID format."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate PDF receipt
            try:
                pdf_buffer = ReceiptService.generate_receipt_pdf(transaction_data, website_name)
                filename = f"receipt_{transaction_data.get('reference_id', transaction_id)}_{timezone.now().strftime('%Y%m%d')}.pdf"
                return ReceiptService.create_pdf_response(pdf_buffer, filename)
            except ImportError as e:
                logger.error(f"PDF generation failed: {str(e)}")
                return Response(
                    {"error": "PDF generation is not available. Please install reportlab: pip install reportlab"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            except Exception as e:
                logger.error(f"Error generating receipt: {str(e)}")
                return Response(
                    {"error": f"Failed to generate receipt: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except (OrderPayment.DoesNotExist, ClientWalletTransaction.DoesNotExist, WalletTransaction.DoesNotExist):
            return Response(
                {"error": "Transaction not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {"error": "Invalid transaction ID."},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], url_path='orders/(?P<order_id>[^/.]+)/initiate')
    def initiate_payment(self, request, order_id=None):
        """
        Initiate payment for a standard order.
        
        Creates a payment record. Gateway integration will be added later.
        For now supports:
        - wallet: Processes immediately
        - manual: Creates pending record for admin processing
        
        Request body:
        {
            "payment_method": "wallet" | "manual" | "stripe" (future),
            "discount_code": "optional_discount_code"
        }
        """
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if order already has completed payment
        if order.payments.filter(status='completed').exists():
            return Response(
                {"error": "Order already has a completed payment."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment_method = request.data.get('payment_method', 'manual')
        discount_code = request.data.get('discount_code')
        
        try:
            payment = OrderPaymentService.create_payment(
                order=order,
                payment_method=payment_method,
                discount_code=discount_code
            )
            
            # Process wallet payment immediately
            if payment_method == 'wallet':
                try:
                    payment = OrderPaymentService.process_wallet_payment(payment)
                    return Response(
                        {
                            "message": "Payment processed successfully.",
                            "payment": TransactionSerializer(payment).data,
                            "payment_identifier": OrderPaymentService.get_payment_identifier(payment)
                        },
                        status=status.HTTP_201_CREATED
                    )
                except Exception as e:
                    logger.error(f"Wallet payment processing failed: {e}")
                    return Response(
                        {"error": f"Payment processing failed: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            elif payment_method == 'smart':
                # Smart payment: wallet → points → gateway
                try:
                    external_gateway = request.data.get('external_gateway', 'stripe')
                    external_id = request.data.get('external_id')
                    
                    result = OrderPaymentService.process_smart_payment(
                        payment=payment,
                        external_gateway=external_gateway,
                        external_id=external_id
                    )
                    
                    response_data = {
                        "message": "Smart payment processed." if result['status'] == 'completed' else "Partial payment processed. Gateway payment pending.",
                        "payment": TransactionSerializer(payment).data,
                        "payment_identifier": OrderPaymentService.get_payment_identifier(payment),
                        "breakdown": {
                            "wallet_amount": float(result['wallet_amount']),
                            "points_used": result['points_used'],
                            "points_amount": float(result['points_amount']),
                            "gateway_amount": float(result['gateway_amount']),
                            "total_paid": float(result['total_paid']),
                            "remaining": float(result['remaining'])
                        },
                        "status": result['status']
                    }
                    
                    if result['status'] == 'pending':
                        response_data["message"] += f" Please complete payment of ${result['remaining']} via {external_gateway}."
                    
                    return Response(
                        response_data,
                        status=status.HTTP_201_CREATED
                    )
                except Exception as e:
                    logger.error(f"Smart payment processing failed: {e}", exc_info=True)
                    return Response(
                        {"error": f"Smart payment processing failed: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                # Manual or gateway payment - return pending payment info
                return Response(
                    {
                        "message": "Payment initiated. Awaiting processing.",
                        "payment": TransactionSerializer(payment).data,
                        "payment_identifier": OrderPaymentService.get_payment_identifier(payment)
                    },
                    status=status.HTTP_201_CREATED
                )
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Payment initiation failed: {e}")
            return Response(
                {"error": f"Payment initiation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update payment status (admin only).
        """
        payment = get_object_or_404(OrderPayment, pk=pk)
        new_status = request.data.get('status')
        
        if new_status not in dict(OrderPayment.STATUS_CHOICES):
            return Response(
                {"error": "Invalid status."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = new_status
        if new_status == 'completed' and not payment.confirmed_at:
            payment.confirmed_at = timezone.now()
        payment.save()
        
        payment_data = TransactionSerializer(payment).data
        payment_data['identifier'] = OrderPaymentService.get_payment_identifier(payment)
        
        return Response(payment_data, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        """
        Get detailed payment information.
        """
        payment = get_object_or_404(OrderPayment, pk=pk)
        payment_obj = TransactionSerializer(payment).data
        payment_obj['identifier'] = OrderPaymentService.get_payment_identifier(payment)
        return Response(payment_obj, status=status.HTTP_200_OK)


# Stub viewsets for other payment-related models
from .models import PaymentNotification, PaymentLog, PaymentDispute, DiscountUsage, AdminLog, PaymentReminderSettings

class PaymentNotificationViewSet(viewsets.ModelViewSet):
    queryset = PaymentNotification.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]

class PaymentLogViewSet(viewsets.ModelViewSet):
    queryset = PaymentLog.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]

class PaymentDisputeViewSet(viewsets.ModelViewSet):
    queryset = PaymentDispute.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]

class DiscountUsageViewSet(viewsets.ModelViewSet):
    queryset = DiscountUsage.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]

class AdminLogViewSet(viewsets.ModelViewSet):
    queryset = AdminLog.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]

class PaymentReminderSettingsViewSet(viewsets.ModelViewSet):
    queryset = PaymentReminderSettings.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = OrderPayment.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = OrderPayment.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]


from .models.payment_reminders import (
    PaymentReminderConfig,
    PaymentReminderSent,
    PaymentReminderDeletionMessage
)
from .serializers import (
    PaymentReminderConfigSerializer,
    PaymentReminderDeletionMessageSerializer,
    PaymentReminderSentSerializer
)
from .services.payment_reminder_service import PaymentReminderService


class PaymentReminderConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payment reminder configurations.
    Admin/Superadmin can create, update, delete reminder configs.
    """
    queryset = PaymentReminderConfig.objects.all().select_related('website', 'created_by')
    serializer_class = PaymentReminderConfigSerializer
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by website if user has website context
        website = getattr(self.request.user, 'website', None)
        if website:
            queryset = queryset.filter(website=website)
        return queryset.order_by('display_order', 'deadline_percentage')

    def perform_create(self, serializer):
        # Set website from user context if not provided
        if 'website' not in serializer.validated_data:
            website = getattr(self.request.user, 'website', None)
            if website:
                serializer.save(website=website, created_by=self.request.user)
            else:
                serializer.save(created_by=self.request.user)
        else:
            serializer.save(created_by=self.request.user)


class PaymentReminderDeletionMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payment deletion messages.
    Admin/Superadmin can create, update, delete deletion messages.
    """
    queryset = PaymentReminderDeletionMessage.objects.all().select_related('website', 'created_by')
    serializer_class = PaymentReminderDeletionMessageSerializer
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by website if user has website context
        website = getattr(self.request.user, 'website', None)
        if website:
            queryset = queryset.filter(website=website)
        return queryset

    def perform_create(self, serializer):
        # Set website from user context if not provided
        if 'website' not in serializer.validated_data:
            website = getattr(self.request.user, 'website', None)
            if website:
                serializer.save(website=website, created_by=self.request.user)
            else:
                serializer.save(created_by=self.request.user)
        else:
            serializer.save(created_by=self.request.user)


class PaymentReminderSentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing sent payment reminders (read-only history).
    """
    queryset = PaymentReminderSent.objects.all().select_related(
        'reminder_config', 'order', 'payment', 'client'
    )
    serializer_class = PaymentReminderSentSerializer
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by website if user has website context
        website = getattr(self.request.user, 'website', None)
        if website:
            queryset = queryset.filter(
                models.Q(order__website=website) | models.Q(payment__website=website)
            )
        return queryset.order_by('-sent_at')
