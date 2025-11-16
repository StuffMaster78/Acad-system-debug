"""
Unified search service for searching across multiple models.
Supports searching orders, users, payments, and messages.
"""
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat
from typing import Dict, List, Any, Optional
from decimal import Decimal

from orders.models import Order
from users.models import User
from order_payments_management.models import OrderPayment
from communications.models import CommunicationMessage, CommunicationThread
from client_wallet.models import ClientWalletTransaction
from writer_wallet.models import WalletTransaction


class UnifiedSearchService:
    """Service for unified search across multiple models."""
    
    @staticmethod
    def search(
        query: str,
        user,
        entity_types: Optional[List[str]] = None,
        limit_per_type: int = 10
    ) -> Dict[str, Any]:
        """
        Search across multiple entity types.
        
        Args:
            query: Search query string
            entity_types: List of entity types to search (orders, users, payments, messages)
                         If None, searches all types
            limit_per_type: Maximum results per entity type
            user: Current user for permission filtering
            
        Returns:
            Dictionary with search results grouped by entity type
        """
        if not query or len(query.strip()) < 2:
            return {
                'orders': [],
                'users': [],
                'payments': [],
                'messages': [],
                'total_results': 0
            }
        
        query = query.strip()
        results = {
            'orders': [],
            'users': [],
            'payments': [],
            'messages': [],
            'total_results': 0
        }
        
        # Determine which entity types to search
        if entity_types is None:
            entity_types = ['orders', 'users', 'payments', 'messages']
        
        # Search Orders
        if 'orders' in entity_types:
            results['orders'] = UnifiedSearchService._search_orders(query, user, limit_per_type)
        
        # Search Users
        if 'users' in entity_types:
            results['users'] = UnifiedSearchService._search_users(query, user, limit_per_type)
        
        # Search Payments
        if 'payments' in entity_types:
            results['payments'] = UnifiedSearchService._search_payments(query, user, limit_per_type)
        
        # Search Messages
        if 'messages' in entity_types:
            results['messages'] = UnifiedSearchService._search_messages(query, user, limit_per_type)
        
        # Calculate total results
        results['total_results'] = (
            len(results['orders']) +
            len(results['users']) +
            len(results['payments']) +
            len(results['messages'])
        )
        
        return results
    
    @staticmethod
    def _search_orders(query: str, user, limit: int) -> List[Dict[str, Any]]:
        """Search orders."""
        user_role = getattr(user, 'role', None)
        
        # Base queryset with role-based filtering
        qs = Order.objects.all()
        
        if user_role == 'client':
            qs = qs.filter(client=user)
        elif user_role == 'writer':
            qs = qs.filter(assigned_writer=user)
        elif user_role not in ['admin', 'superadmin', 'support', 'editor']:
            qs = qs.none()
        
        # Search across multiple fields
        search_q = (
            Q(topic__icontains=query) |
            Q(id__icontains=query) |
            Q(order_instructions__icontains=query) |
            Q(reference_id__icontains=query) if hasattr(Order, 'reference_id') else Q()
        )
        
        # Try to parse as order ID
        try:
            order_id = int(query)
            search_q |= Q(id=order_id)
        except ValueError:
            pass
        
        orders = qs.filter(search_q).select_related(
            'client', 'assigned_writer', 'paper_type', 'website'
        )[:limit]
        
        return [
            {
                'id': order.id,
                'type': 'order',
                'title': order.topic or f'Order #{order.id}',
                'subtitle': f"Status: {order.status} | Client: {order.client.username if order.client else 'N/A'}",
                'url': f'/orders/{order.id}',
                'status': order.status,
                'amount': float(order.total_price) if order.total_price else None,
                'created_at': order.created_at.isoformat() if order.created_at else None,
            }
            for order in orders
        ]
    
    @staticmethod
    def _search_users(query: str, user, limit: int) -> List[Dict[str, Any]]:
        """Search users."""
        user_role = getattr(user, 'role', None)
        
        # Only admin/superadmin can search users
        if user_role not in ['admin', 'superadmin']:
            return []
        
        # Search across username, email, registration_id
        search_q = (
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )
        
        # Try to parse as user ID
        try:
            user_id = int(query)
            search_q |= Q(id=user_id)
        except ValueError:
            pass
        
        # Check for registration_id in profiles
        from users.models import ClientProfile, WriterProfile
        client_profiles = ClientProfile.objects.filter(registration_id__icontains=query).values_list('user_id', flat=True)
        writer_profiles = WriterProfile.objects.filter(registration_id__icontains=query).values_list('user_id', flat=True)
        if client_profiles.exists() or writer_profiles.exists():
            search_q |= Q(id__in=list(client_profiles) + list(writer_profiles))
        
        users = User.objects.filter(search_q).select_related('client_profile', 'writer_profile')[:limit]
        
        return [
            {
                'id': user_obj.id,
                'type': 'user',
                'title': user_obj.username or user_obj.email,
                'subtitle': f"Role: {user_obj.role} | Email: {user_obj.email if user_role in ['admin', 'superadmin'] else '***'}",
                'url': f'/admin/users/{user_obj.id}',
                'role': user_obj.role,
                'email': user_obj.email if user_role in ['admin', 'superadmin'] else None,
                'created_at': user_obj.date_joined.isoformat() if user_obj.date_joined else None,
            }
            for user_obj in users
        ]
    
    @staticmethod
    def _search_payments(query: str, user, limit: int) -> List[Dict[str, Any]]:
        """Search payments."""
        user_role = getattr(user, 'role', None)
        
        results = []
        
        # Search OrderPayments
        order_payments = OrderPayment.objects.all()
        if user_role == 'client':
            order_payments = order_payments.filter(client=user)
        elif user_role not in ['admin', 'superadmin', 'support']:
            order_payments = order_payments.none()
        
        search_q = (
            Q(reference_id__icontains=query) |
            Q(transaction_id__icontains=query)
        )
        
        try:
            payment_id = int(query)
            search_q |= Q(id=payment_id)
        except ValueError:
            pass
        
        payments = order_payments.filter(search_q).select_related('client', 'order', 'website')[:limit]
        
        for payment in payments:
            results.append({
                'id': f'order_payment_{payment.id}',
                'type': 'payment',
                'title': f"Payment #{payment.reference_id or payment.id}",
                'subtitle': f"Amount: ${payment.amount} | Status: {payment.status}",
                'url': f'/payments/{payment.id}',
                'amount': float(payment.amount),
                'status': payment.status,
                'created_at': payment.created_at.isoformat() if payment.created_at else None,
            })
        
        # Search Wallet Transactions (if admin/superadmin)
        if user_role in ['admin', 'superadmin']:
            wallet_transactions = ClientWalletTransaction.objects.filter(
                Q(transaction_reference__icontains=query) |
                Q(id__icontains=query)
            ).select_related('wallet__user')[:limit]
            
            for transaction in wallet_transactions:
                results.append({
                    'id': f'client_wallet_{transaction.id}',
                    'type': 'payment',
                    'title': f"Wallet Transaction #{transaction.transaction_reference or transaction.id}",
                    'subtitle': f"Amount: ${transaction.amount} | Type: {'Credit' if transaction.is_credit else 'Debit'}",
                    'url': f'/payments/history',
                    'amount': float(transaction.amount),
                    'status': 'completed',
                    'created_at': transaction.created_at.isoformat() if transaction.created_at else None,
                })
        
        return results[:limit]
    
    @staticmethod
    def _search_messages(query: str, user, limit: int) -> List[Dict[str, Any]]:
        """Search messages."""
        user_role = getattr(user, 'role', None)
        
        # Search messages in threads user has access to
        threads = CommunicationThread.objects.filter(participants=user)
        messages = CommunicationMessage.objects.filter(
            thread__in=threads,
            message__icontains=query,
            is_deleted=False
        ).select_related('sender', 'thread__order')[:limit]
        
        return [
            {
                'id': message.id,
                'type': 'message',
                'title': message.message[:100] + ('...' if len(message.message) > 100 else ''),
                'subtitle': f"From: {message.sender.username if message.sender else 'System'} | Order: #{message.thread.order.id if message.thread.order else 'N/A'}",
                'url': f"/orders/{message.thread.order.id}#messages" if message.thread.order else '/messages',
                'sender': message.sender.username if message.sender else 'System',
                'created_at': message.sent_at.isoformat() if message.sent_at else None,
            }
            for message in messages
        ]

