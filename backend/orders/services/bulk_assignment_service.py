"""
Bulk Assignment Service

Allows assigning multiple orders to writers with intelligent workload distribution.
"""
from typing import List, Dict, Optional, Tuple
from django.db import transaction
from django.db.models import Count, Q
from django.core.exceptions import ValidationError
from django.utils import timezone

from orders.models import Order, OrderStatus
from orders.services.assignment import OrderAssignmentService
from orders.services.auto_assignment_service import AutoAssignmentService
from writer_management.models.profile import WriterProfile
from writer_management.models.levels import WriterLevel


class BulkAssignmentService:
    """
    Service for bulk assignment of orders to writers.
    """
    
    @staticmethod
    @transaction.atomic
    def assign_orders_to_writers(
        assignments: List[Dict],
        actor,
        require_acceptance: bool = True,
    ) -> Dict:
        """
        Assign multiple orders to writers.
        
        Args:
            assignments: List of dicts with 'order_id' and 'writer_id'
            actor: User performing assignments
            require_acceptance: Whether writers need to accept
            
        Returns:
            Dictionary with assignment results
        """
        results = {
            'total': len(assignments),
            'successful': 0,
            'failed': 0,
            'assignments': [],
            'errors': [],
        }
        
        for assignment in assignments:
            order_id = assignment.get('order_id')
            writer_id = assignment.get('writer_id')
            reason = assignment.get('reason', 'Bulk assignment')
            writer_payment_amount = assignment.get('writer_payment_amount')
            
            if not order_id or not writer_id:
                results['failed'] += 1
                results['errors'].append({
                    'assignment': assignment,
                    'error': 'Missing order_id or writer_id',
                })
                continue
            
            try:
                order = Order.objects.get(id=order_id)
                assignment_service = OrderAssignmentService(order)
                assignment_service.actor = actor
                
                updated_order = assignment_service.assign_writer(
                    writer_id=writer_id,
                    reason=reason,
                    writer_payment_amount=writer_payment_amount,
                )
                
                results['successful'] += 1
                results['assignments'].append({
                    'order_id': order_id,
                    'writer_id': writer_id,
                    'status': 'assigned',
                })
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'order_id': order_id,
                    'writer_id': writer_id,
                    'error': str(e),
                })
        
        return results
    
    @staticmethod
    @transaction.atomic
    def distribute_orders_automatically(
        orders: List[Order],
        actor,
        strategy: str = 'balanced',
        min_rating: float = 4.0,
    ) -> Dict:
        """
        Automatically distribute orders to writers using various strategies.
        
        Args:
            orders: List of orders to assign
            actor: User performing assignments
            strategy: Distribution strategy ('balanced', 'round_robin', 'best_match')
            min_rating: Minimum writer rating
            
        Returns:
            Dictionary with distribution results
        """
        if strategy == 'balanced':
            return BulkAssignmentService._balanced_distribution(orders, actor, min_rating)
        elif strategy == 'round_robin':
            return BulkAssignmentService._round_robin_distribution(orders, actor, min_rating)
        elif strategy == 'best_match':
            return BulkAssignmentService._best_match_distribution(orders, actor, min_rating)
        else:
            raise ValidationError(f"Unknown distribution strategy: {strategy}")
    
    @staticmethod
    def _balanced_distribution(orders: List[Order], actor, min_rating: float) -> Dict:
        """
        Distribute orders to balance workload across all writers.
        """
        results = {
            'total': len(orders),
            'successful': 0,
            'failed': 0,
            'assignments': [],
            'errors': [],
        }
        
        # Get available writers with workload info
        writers = BulkAssignmentService._get_available_writers_with_workload(min_rating)
        
        if not writers:
            results['errors'].append({
                'error': 'No available writers found',
            })
            return results
        
        # Sort orders by priority (urgent first, then by creation date)
        sorted_orders = sorted(
            orders,
            key=lambda o: (
                BulkAssignmentService._is_urgent(o),  # Urgent first (True < False)
                o.created_at  # Then by creation date
            ),
            reverse=True
        )
        
        # Distribute orders
        writer_index = 0
        for order in sorted_orders:
            if not writers:
                results['failed'] += 1
                results['errors'].append({
                    'order_id': order.id,
                    'error': 'No available writers',
                })
                continue
            
            # Get next writer (round-robin with workload consideration)
            writer = writers[writer_index % len(writers)]
            
            try:
                # Try to assign
                assignment_service = OrderAssignmentService(order)
                assignment_service.actor = actor
                
                updated_order = assignment_service.assign_writer(
                    writer_id=writer['writer'].id,
                    reason="Bulk balanced distribution",
                )
                
                results['successful'] += 1
                results['assignments'].append({
                    'order_id': order.id,
                    'writer_id': writer['writer'].id,
                    'writer_username': writer['writer'].username,
                })
                
                # Update writer workload
                writer['active_orders'] += 1
                
                # Move to next writer
                writer_index += 1
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'order_id': order.id,
                    'error': str(e),
                })
                # Try next writer
                writer_index += 1
        
        return results
    
    @staticmethod
    def _round_robin_distribution(orders: List[Order], actor, min_rating: float) -> Dict:
        """
        Distribute orders in round-robin fashion.
        """
        results = {
            'total': len(orders),
            'successful': 0,
            'failed': 0,
            'assignments': [],
            'errors': [],
        }
        
        writers = BulkAssignmentService._get_available_writers_with_workload(min_rating)
        
        if not writers:
            results['errors'].append({
                'error': 'No available writers found',
            })
            return results
        
        writer_index = 0
        for order in orders:
            writer = writers[writer_index % len(writers)]
            
            try:
                assignment_service = OrderAssignmentService(order)
                assignment_service.actor = actor
                
                updated_order = assignment_service.assign_writer(
                    writer_id=writer['writer'].id,
                    reason="Bulk round-robin distribution",
                )
                
                results['successful'] += 1
                results['assignments'].append({
                    'order_id': order.id,
                    'writer_id': writer['writer'].id,
                })
                
                writer_index += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'order_id': order.id,
                    'error': str(e),
                })
                writer_index += 1
        
        return results
    
    @staticmethod
    def _best_match_distribution(orders: List[Order], actor, min_rating: float) -> Dict:
        """
        Distribute orders using best match (auto-assignment) for each order.
        """
        results = {
            'total': len(orders),
            'successful': 0,
            'failed': 0,
            'assignments': [],
            'errors': [],
        }
        
        for order in orders:
            try:
                auto_service = AutoAssignmentService(order, actor=actor)
                updated_order, writer, info = auto_service.auto_assign(
                    reason="Bulk best-match distribution",
                    require_acceptance=True,
                    min_rating=min_rating,
                )
                
                results['successful'] += 1
                results['assignments'].append({
                    'order_id': order.id,
                    'writer_id': writer.id,
                    'writer_username': writer.username,
                    'assignment_info': info,
                })
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'order_id': order.id,
                    'error': str(e),
                })
        
        return results
    
    @staticmethod
    def _get_available_writers_with_workload(min_rating: float) -> List[Dict]:
        """Get available writers with their current workload."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        writers = User.objects.filter(
            role='writer',
            is_active=True,
            writer_profile__is_available_for_auto_assignments=True,
            writer_profile__is_deleted=False,
        ).annotate(
            avg_rating=Avg('orders_as_writer__rating'),
            active_orders=Count(
                'orders_as_writer',
                filter=Q(
                    orders_as_writer__status__in=[
                        OrderStatus.IN_PROGRESS.value,
                        OrderStatus.ON_HOLD.value,
                        OrderStatus.REVISION_REQUESTED.value,
                    ],
                    orders_as_writer__is_deleted=False,
                )
            ),
        ).filter(
            avg_rating__gte=min_rating,
        ).select_related('writer_profile', 'writer_profile__writer_level')
        
        writer_list = []
        for writer in writers:
            max_orders = 5  # Default
            if writer.writer_profile and writer.writer_profile.writer_level:
                max_orders = writer.writer_profile.writer_level.max_orders or 5
            
            active = writer.active_orders or 0
            
            # Only include writers with capacity
            if active < max_orders:
                writer_list.append({
                    'writer': writer,
                    'active_orders': active,
                    'max_orders': max_orders,
                    'capacity': max_orders - active,
                })
        
        # Sort by capacity (writers with more capacity first)
        writer_list.sort(key=lambda x: x['capacity'], reverse=True)
        return writer_list
    
    @staticmethod
    def _is_urgent(order: Order) -> bool:
        """Check if order is urgent."""
        if not order.client_deadline:
            return False
        
        time_until_deadline = order.client_deadline - timezone.now()
        hours_until_deadline = time_until_deadline.total_seconds() / 3600.0
        return hours_until_deadline < 24.0

