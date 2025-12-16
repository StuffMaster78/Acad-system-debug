"""
Auto-Assignment Service for Orders

Automatically assigns writers to orders based on:
- Writer expertise (subject, paper type)
- Writer rating
- Writer availability
- Workload balancing
"""
from decimal import Decimal
from typing import Optional, List, Dict, Tuple
from django.db import transaction
from django.db.models import Count, Avg, Q, F
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model

from orders.models import Order, OrderStatus
from orders.services.assignment import OrderAssignmentService
from orders.services.order_access_service import OrderAccessService
from writer_management.models.profile import WriterProfile
from writer_management.models.levels import WriterLevel
from notifications_system.services.core import NotificationService

User = get_user_model()


class AutoAssignmentService:
    """
    Service for automatically assigning writers to orders.
    """
    
    def __init__(self, order: Order, actor=None):
        """
        Initialize the auto-assignment service.
        
        Args:
            order: The order to assign
            actor: User performing the assignment (for logging)
        """
        self.order = order
        self.actor = actor
    
    def find_best_writer(
        self,
        max_candidates: int = 10,
        min_rating: float = 4.0,
        require_subject_match: bool = True,
        require_paper_type_match: bool = False,
    ) -> Optional[User]:
        """
        Find the best writer for the order based on multiple criteria.
        
        Args:
            max_candidates: Maximum number of candidates to evaluate
            min_rating: Minimum average rating required
            require_subject_match: Whether to require subject expertise match
            require_paper_type_match: Whether to require paper type match
            
        Returns:
            Best matching writer, or None if no suitable writer found
        """
        # Get base queryset of available writers
        writers = self._get_base_writer_queryset(min_rating)
        
        # Apply filters
        if require_subject_match and self.order.subject:
            writers = self._filter_by_subject(writers)
        
        if require_paper_type_match and self.order.paper_type:
            writers = self._filter_by_paper_type(writers)
        
        # Annotate with scoring metrics
        writers = self._annotate_writer_metrics(writers)
        
        # Score and rank writers
        scored_writers = self._score_writers(writers[:max_candidates])
        
        if not scored_writers:
            return None
        
        # Return top-scored writer
        return scored_writers[0]['writer']
    
    def _get_base_writer_queryset(self, min_rating: float):
        """Get base queryset of available writers."""
        return User.objects.filter(
            role='writer',
            is_active=True,
            writer_profile__is_available_for_auto_assignments=True,
            writer_profile__is_deleted=False,
        ).annotate(
            avg_rating=Avg('orders_as_writer__rating'),
            active_orders_count=Count(
                'orders_as_writer',
                filter=Q(
                    orders_as_writer__status__in=[
                        OrderStatus.IN_PROGRESS.value,
                        OrderStatus.ON_HOLD.value,
                        OrderStatus.REVISION_REQUESTED.value,
                        OrderStatus.UNDER_EDITING.value,
                    ],
                    orders_as_writer__is_deleted=False,
                )
            ),
            completed_orders_count=Count(
                'orders_as_writer',
                filter=Q(
                    orders_as_writer__status=OrderStatus.COMPLETED.value,
                    orders_as_writer__is_deleted=False,
                )
            ),
        ).filter(
            avg_rating__gte=min_rating,
        ).select_related('writer_profile', 'writer_profile__writer_level')
    
    def _filter_by_subject(self, writers):
        """Filter writers by subject expertise."""
        if not self.order.subject:
            return writers
        
        # Writers who have completed orders in this subject
        subject_writer_ids = Order.objects.filter(
            assigned_writer__in=writers,
            subject=self.order.subject,
            status=OrderStatus.COMPLETED.value,
            is_deleted=False,
        ).values_list('assigned_writer_id', flat=True).distinct()
        
        # Also check portfolio specialties if available
        from writer_management.models.portfolio import WriterPortfolio
        portfolio_writer_ids = WriterPortfolio.objects.filter(
            writer__in=writers,
            specialties=self.order.subject,
            is_enabled=True,
        ).values_list('writer_id', flat=True).distinct()
        
        # Combine both
        matching_ids = set(subject_writer_ids) | set(portfolio_writer_ids)
        
        if matching_ids:
            return writers.filter(id__in=matching_ids)
        else:
            # If no exact match, return all (subject match not strict)
            return writers
    
    def _filter_by_paper_type(self, writers):
        """Filter writers by paper type expertise."""
        if not self.order.paper_type:
            return writers
        
        # Writers who have completed orders with this paper type
        paper_type_writer_ids = Order.objects.filter(
            assigned_writer__in=writers,
            paper_type=self.order.paper_type,
            status=OrderStatus.COMPLETED.value,
            is_deleted=False,
        ).values_list('assigned_writer_id', flat=True).distinct()
        
        if paper_type_writer_ids:
            return writers.filter(id__in=paper_type_writer_ids)
        else:
            # If no exact match, return all (paper type match not strict)
            return writers
    
    def _annotate_writer_metrics(self, writers):
        """Annotate writers with performance metrics."""
        return writers.annotate(
            # Total assignments (for acceptance rate calculation)
            total_assignments=Count('assignment_acceptances'),
            accepted_assignments=Count(
                'assignment_acceptances',
                filter=Q(assignment_acceptances__status='accepted')
            ),
        )
    
    def _score_writers(self, writers) -> List[Dict]:
        """
        Score writers based on multiple criteria.
        
        Scoring factors:
        1. Rating (0-5) - 30% weight
        2. Workload balance (inverse of active orders) - 25% weight
        3. Subject expertise match - 20% weight
        4. On-time delivery rate - 15% weight
        5. Response time (faster is better) - 10% weight
        """
        scored = []
        
        for writer in writers:
            score = 0.0
            
            # 1. Rating (0-5 scale, normalized to 0-1)
            rating = float(writer.avg_rating or 0)
            rating_score = min(rating / 5.0, 1.0) * 0.30
            score += rating_score
            
            # 2. Workload balance (inverse of active orders, normalized)
            # Get max orders from writer level
            max_orders = 5  # Default
            if writer.writer_profile and writer.writer_profile.writer_level:
                max_orders = writer.writer_profile.writer_level.max_orders or 5
            
            active = writer.active_orders_count or 0
            if max_orders > 0:
                workload_ratio = 1.0 - (active / max_orders)
                workload_score = max(0, workload_ratio) * 0.25
                score += workload_score
            
            # 3. Subject expertise (binary: has experience or not)
            has_subject_expertise = False
            if self.order.subject:
                # Check if writer has completed orders in this subject
                has_subject_expertise = Order.objects.filter(
                    assigned_writer=writer,
                    subject=self.order.subject,
                    status=OrderStatus.COMPLETED.value,
                    is_deleted=False,
                ).exists()
            
            expertise_score = (1.0 if has_subject_expertise else 0.5) * 0.20
            score += expertise_score
            
            # 4. Acceptance rate (how often writer accepts assignments)
            total_assigns = writer.total_assignments or 1
            accepted = writer.accepted_assignments or 0
            acceptance_rate = accepted / total_assigns if total_assigns > 0 else 0.5
            acceptance_score = acceptance_rate * 0.15
            score += acceptance_score
            
            # 5. Experience (completed orders count, normalized)
            completed = writer.completed_orders_count or 0
            # Normalize: 0 orders = 0.0, 50+ orders = 1.0
            experience_score = min(1.0, completed / 50.0) * 0.10
            score += experience_score
            
            scored.append({
                'writer': writer,
                'score': score,
                'rating': rating,
                'active_orders': active,
                'has_subject_expertise': has_subject_expertise,
                'acceptance_rate': acceptance_rate,
                'completed_orders': completed,
            })
        
        # Sort by score (descending)
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored
    
    @transaction.atomic
    def auto_assign(
        self,
        reason: str = "Auto-assigned by system",
        require_acceptance: bool = True,
        max_candidates: int = 10,
        min_rating: float = 4.0,
    ) -> Tuple[Order, Optional[User], Dict]:
        """
        Automatically assign a writer to the order.
        
        Args:
            reason: Reason for assignment
            require_acceptance: Whether writer needs to accept (True) or direct assignment (False)
            max_candidates: Maximum candidates to evaluate
            min_rating: Minimum rating required
            
        Returns:
            Tuple of (updated_order, assigned_writer, assignment_info)
            
        Raises:
            ValidationError: If no suitable writer found or assignment fails
        """
        # Validate order is assignable
        if self.order.status not in [OrderStatus.AVAILABLE.value, OrderStatus.PAID.value]:
            raise ValidationError(
                f"Order #{self.order.id} is not in an assignable status. "
                f"Current status: {self.order.status}"
            )
        
        if self.order.assigned_writer:
            raise ValidationError(
                f"Order #{self.order.id} is already assigned to a writer."
            )
        
        # Find best writer
        writer = self.find_best_writer(
            max_candidates=max_candidates,
            min_rating=min_rating,
            require_subject_match=True,
            require_paper_type_match=False,
        )
        
        if not writer:
            raise ValidationError(
                f"No suitable writer found for Order #{self.order.id}. "
                "Try adjusting criteria or assign manually."
            )
        
        # Validate writer can be assigned
        can_assign = OrderAccessService.can_be_assigned(
            writer=writer,
            order=self.order,
            by_admin=False  # Auto-assignment doesn't override
        )
        
        if not can_assign:
            raise ValidationError(
                f"Writer {writer.username} does not meet level requirements for Order #{self.order.id}."
            )
        
        # Perform assignment
        assignment_service = OrderAssignmentService(self.order)
        assignment_service.actor = self.actor
        
        try:
            updated_order = assignment_service.assign_writer(
                writer_id=writer.id,
                reason=reason,
                writer_payment_amount=None  # Use level-based calculation
            )
            
            assignment_info = {
                'writer_id': writer.id,
                'writer_username': writer.username,
                'assignment_method': 'auto',
                'score': self._get_writer_score(writer),
                'candidates_evaluated': max_candidates,
            }
            
            # Log auto-assignment
            from audit_logging.services.audit_log_service import AuditLogService
            AuditLogService.log_auto(
                actor=self.actor,
                action="AUTO_ASSIGN",
                target="orders.Order",
                target_id=self.order.id,
                metadata={
                    "writer_id": writer.id,
                    "assignment_info": assignment_info,
                }
            )
            
            return updated_order, writer, assignment_info
            
        except Exception as e:
            raise ValidationError(
                f"Failed to auto-assign writer: {str(e)}"
            )
    
    def _get_writer_score(self, writer: User) -> float:
        """Get the score for a specific writer (for logging)."""
        # This is a simplified version - in production, you'd recalculate
        return float(writer.avg_rating or 0)
    
    @staticmethod
    def auto_assign_available_orders(
        website=None,
        max_assignments: int = 10,
        min_rating: float = 4.0,
        actor=None,
    ) -> Dict:
        """
        Auto-assign multiple available orders.
        
        Args:
            website: Website to filter orders (optional)
            max_assignments: Maximum number of orders to assign
            min_rating: Minimum writer rating
            actor: User performing the action (for logging)
            
        Returns:
            Dictionary with assignment results
        """
        # Get available orders
        orders = Order.objects.filter(
            status__in=[OrderStatus.AVAILABLE.value, OrderStatus.PAID.value],
            assigned_writer__isnull=True,
            is_deleted=False,
        )
        
        if website:
            orders = orders.filter(website=website)
        
        orders = orders.order_by('-created_at')[:max_assignments]
        
        results = {
            'total_orders': orders.count(),
            'successful': 0,
            'failed': 0,
            'assignments': [],
            'errors': [],
        }
        
        for order in orders:
            try:
                service = AutoAssignmentService(order, actor=actor)
                updated_order, writer, info = service.auto_assign(
                    reason="Bulk auto-assignment",
                    require_acceptance=True,
                    min_rating=min_rating,
                )
                
                results['successful'] += 1
                results['assignments'].append({
                    'order_id': order.id,
                    'writer_id': writer.id,
                    'writer_username': writer.username,
                    'info': info,
                })
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'order_id': order.id,
                    'error': str(e),
                })
        
        return results

