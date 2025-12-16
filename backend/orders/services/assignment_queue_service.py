"""
Assignment Queue Service

Implements a priority queue system for order assignments based on:
- Writer rating
- Writer response time
- Writer success rate
- Order urgency
"""
from decimal import Decimal
from typing import List, Dict, Optional
from django.db import transaction
from django.db.models import Count, Avg, Q, F, ExpressionWrapper, DurationField
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from orders.models import Order, OrderRequest, OrderRequestStatus, OrderStatus
from writer_management.models.profile import WriterProfile
from writer_management.models.levels import WriterLevel


class AssignmentQueueService:
    """
    Service for managing priority-based assignment queues.
    """
    
    @staticmethod
    def get_prioritized_requests_for_order(order: Order) -> List[Dict]:
        """
        Get writer requests for an order, prioritized by multiple factors.
        
        Priority factors:
        1. Writer rating (higher = better) - 30%
        2. Response time (faster = better) - 25%
        3. Success rate (higher = better) - 25%
        4. Order urgency (urgent orders prioritize experienced writers) - 20%
        
        Returns:
            List of request dictionaries with priority scores, sorted by priority
        """
        requests = OrderRequest.objects.filter(
            order=order,
            status=OrderRequestStatus.PENDING,
        ).select_related('writer', 'writer__writer_profile', 'writer__writer_profile__writer_level')
        
        if not requests.exists():
            return []
        
        # Annotate requests with writer metrics
        annotated_requests = requests.annotate(
            # Writer rating
            writer_rating=Avg('writer__orders_as_writer__rating'),
            
            # Average response time (time from request to acceptance)
            avg_response_time=Avg(
                ExpressionWrapper(
                    F('accepted_by_admin_at') - F('created_at'),
                    output_field=DurationField()
                ),
                filter=Q(status=OrderRequestStatus.ACCEPTED)
            ),
            
            # Success rate (completed orders / total assigned orders)
            total_assigned=Count(
                'writer__orders_as_writer',
                filter=Q(writer__orders_as_writer__is_deleted=False)
            ),
            completed_orders=Count(
                'writer__orders_as_writer',
                filter=Q(
                    writer__orders_as_writer__status=OrderStatus.COMPLETED.value,
                    writer__orders_as_writer__is_deleted=False
                )
            ),
            
            # Active workload
            active_workload=Count(
                'writer__orders_as_writer',
                filter=Q(
                    writer__orders_as_writer__status__in=[
                        OrderStatus.IN_PROGRESS.value,
                        OrderStatus.ON_HOLD.value,
                        OrderStatus.REVISION_REQUESTED.value,
                    ],
                    writer__orders_as_writer__is_deleted=False
                )
            ),
        )
        
        # Calculate priority scores
        prioritized = []
        is_urgent = AssignmentQueueService._is_urgent_order(order)
        
        for request in annotated_requests:
            score = 0.0
            
            # 1. Rating (0-5 scale, normalized to 0-1)
            rating = float(request.writer_rating or 0)
            rating_score = min(rating / 5.0, 1.0) * 0.30
            score += rating_score
            
            # 2. Response time (faster is better)
            # Average response time in hours (default 24 hours)
            avg_response_hours = 24.0
            if request.avg_response_time:
                total_seconds = request.avg_response_time.total_seconds()
                avg_response_hours = total_seconds / 3600.0
            
            # Normalize: 0 hours = 1.0, 48+ hours = 0.0
            response_score = max(0, 1.0 - (avg_response_hours / 48.0)) * 0.25
            score += response_score
            
            # 3. Success rate (completed / total assigned)
            total = request.total_assigned or 1
            completed = request.completed_orders or 0
            success_rate = completed / total if total > 0 else 0.5
            success_score = success_rate * 0.25
            score += success_score
            
            # 4. Order urgency + writer experience
            # For urgent orders, prioritize experienced writers
            # For normal orders, balance workload
            if is_urgent:
                # Urgent: prioritize by experience (completed orders)
                experience = completed
                experience_normalized = min(1.0, experience / 50.0)
                urgency_score = experience_normalized * 0.20
            else:
                # Normal: prioritize by workload balance (less active = better)
                max_orders = 5  # Default
                if request.writer.writer_profile and request.writer.writer_profile.writer_level:
                    max_orders = request.writer.writer_profile.writer_level.max_orders or 5
                
                active = request.active_workload or 0
                if max_orders > 0:
                    workload_ratio = 1.0 - (active / max_orders)
                    urgency_score = max(0, workload_ratio) * 0.20
                else:
                    urgency_score = 0.0
            
            score += urgency_score
            
            prioritized.append({
                'request': request,
                'writer': request.writer,
                'score': score,
                'rating': rating,
                'avg_response_hours': avg_response_hours,
                'success_rate': success_rate,
                'active_workload': request.active_workload or 0,
                'completed_orders': completed,
            })
        
        # Sort by score (descending)
        prioritized.sort(key=lambda x: x['score'], reverse=True)
        return prioritized
    
    @staticmethod
    def _is_urgent_order(order: Order) -> bool:
        """Check if order is urgent based on deadline proximity."""
        if not order.client_deadline:
            return False
        
        time_until_deadline = order.client_deadline - timezone.now()
        hours_until_deadline = time_until_deadline.total_seconds() / 3600.0
        
        # Consider urgent if less than 24 hours remaining
        return hours_until_deadline < 24.0
    
    @staticmethod
    def get_top_priority_request(order: Order) -> Optional[OrderRequest]:
        """
        Get the highest priority request for an order.
        
        Returns:
            Highest priority OrderRequest, or None if no requests
        """
        prioritized = AssignmentQueueService.get_prioritized_requests_for_order(order)
        if not prioritized:
            return None
        
        return prioritized[0]['request']
    
    @staticmethod
    @transaction.atomic
    def assign_from_queue(
        order: Order,
        actor,
        use_priority: bool = True,
    ) -> Order:
        """
        Assign order from request queue using priority system.
        
        Args:
            order: Order to assign
            actor: User performing assignment
            use_priority: Whether to use priority queue (True) or first-come-first-served (False)
            
        Returns:
            Updated order
            
        Raises:
            ValidationError: If no requests available
        """
        if use_priority:
            # Use priority queue
            prioritized = AssignmentQueueService.get_prioritized_requests_for_order(order)
            if not prioritized:
                raise ValidationError(f"No pending requests for Order #{order.id}")
            
            top_request = prioritized[0]['request']
            writer = top_request.writer
        else:
            # First-come-first-served
            request = OrderRequest.objects.filter(
                order=order,
                status=OrderRequestStatus.PENDING,
            ).order_by('created_at').first()
            
            if not request:
                raise ValidationError(f"No pending requests for Order #{order.id}")
            
            writer = request.writer
            top_request = request
        
        # Assign using OrderRequestService
        from orders.services.order_request_service import OrderRequestService
        service = OrderRequestService(user=actor)
        service.accept_writer(order, writer)
        
        return order
    
    @staticmethod
    def get_queue_statistics(order: Order) -> Dict:
        """
        Get statistics about the request queue for an order.
        
        Returns:
            Dictionary with queue statistics
        """
        requests = OrderRequest.objects.filter(
            order=order,
            status=OrderRequestStatus.PENDING,
        )
        
        prioritized = AssignmentQueueService.get_prioritized_requests_for_order(order)
        
        return {
            'total_requests': requests.count(),
            'prioritized_count': len(prioritized),
            'top_writer': prioritized[0]['writer'].username if prioritized else None,
            'top_score': prioritized[0]['score'] if prioritized else None,
            'is_urgent': AssignmentQueueService._is_urgent_order(order),
            'requests': [
                {
                    'writer_id': item['writer'].id,
                    'writer_username': item['writer'].username,
                    'score': item['score'],
                    'rating': item['rating'],
                    'success_rate': item['success_rate'],
                }
                for item in prioritized[:5]  # Top 5
            ],
        }

