"""
Service to check if a writer qualifies for level progression based on WriterLevel requirements.
"""

from typing import Tuple, List
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class WriterLevelProgressionService:
    """
    Checks if a writer qualifies for level progression.
    """
    
    @staticmethod
    def check_level_eligibility(
        writer,
        target_level
    ) -> Tuple[bool, List[str]]:
        """
        Check if writer meets requirements for target level.
        
        Args:
            writer: WriterProfile instance
            target_level: WriterLevel instance to check eligibility for
            
        Returns:
            Tuple of (is_eligible, list_of_failed_requirements)
        """
        failed_requirements = []
        
        # Get writer stats
        stats = WriterLevelProgressionService._get_writer_stats(writer)
        
        # Check minimum orders
        if stats['total_completed_orders'] < target_level.min_orders_to_attain:
            failed_requirements.append(
                f"Need {target_level.min_orders_to_attain} completed orders "
                f"(currently have {stats['total_completed_orders']})"
            )
        
        # Check minimum rating
        if stats['avg_rating'] < target_level.min_rating_to_attain:
            failed_requirements.append(
                f"Need {target_level.min_rating_to_attain:.2f} average rating "
                f"(currently {stats['avg_rating']:.2f})"
            )
        
        # Check minimum takes
        if stats['total_takes'] < target_level.min_takes_to_attain:
            failed_requirements.append(
                f"Need {target_level.min_takes_to_attain} successful takes "
                f"(currently have {stats['total_takes']})"
            )
        
        # Check completion rate
        if stats['completion_rate'] < target_level.min_completion_rate:
            failed_requirements.append(
                f"Need {target_level.min_completion_rate:.2f}% completion rate "
                f"(currently {stats['completion_rate']:.2f}%)"
            )
        
        # Check revision rate
        if target_level.max_revision_rate is not None:
            if stats['revision_rate'] > target_level.max_revision_rate:
                failed_requirements.append(
                    f"Revision rate must be below {target_level.max_revision_rate:.2f}% "
                    f"(currently {stats['revision_rate']:.2f}%)"
                )
        
        # Check lateness rate
        if target_level.max_lateness_rate is not None:
            if stats['lateness_rate'] > target_level.max_lateness_rate:
                failed_requirements.append(
                    f"Lateness rate must be below {target_level.max_lateness_rate:.2f}% "
                    f"(currently {stats['lateness_rate']:.2f}%)"
                )
        
        return len(failed_requirements) == 0, failed_requirements
    
    @staticmethod
    def _get_writer_stats(writer):
        """
        Get current writer statistics for level progression checking.
        
        Args:
            writer: WriterProfile instance
            
        Returns:
            dict with writer statistics
        """
        from orders.models import Order
        from writer_management.models.metrics import WriterPerformanceMetrics
        
        # Get latest metrics if available
        try:
            metrics = WriterPerformanceMetrics.objects.filter(
                writer=writer
            ).order_by('-created_at').first()
            
            if metrics:
                return {
                    'total_completed_orders': writer.completed_orders or 0,
                    'total_takes': writer.number_of_takes or 0,
                    'avg_rating': float(metrics.avg_rating or 0),
                    'completion_rate': float(metrics.completion_rate * 100 if hasattr(metrics, 'completion_rate') and metrics.completion_rate else 0),
                    'revision_rate': float(metrics.revision_rate * 100 if hasattr(metrics, 'revision_rate') and metrics.revision_rate else 0),
                    'lateness_rate': float(metrics.lateness_rate * 100 if hasattr(metrics, 'lateness_rate') and metrics.lateness_rate else 0),
                }
        except Exception as e:
            logger.warning(f"Error fetching metrics for writer {writer.id}: {e}")
        
        # Fallback: calculate from orders
        orders = Order.objects.filter(assigned_writer=writer.user)
        # Include both 'completed' and 'revised' statuses as completed orders
        from orders.order_enums import OrderStatus
        completed_orders = orders.filter(status__in=[OrderStatus.COMPLETED.value, OrderStatus.REVISED.value])
        total_orders = orders.count()
        
        # Calculate completion rate
        completion_rate = (completed_orders.count() / total_orders * 100) if total_orders > 0 else 0
        
        # Calculate average rating from reviews
        # Order model has a 'reviews' relationship (related_name from OrderReview)
        # We need to get ratings from the reviews
        from reviews_system.models.order_review import OrderReview
        from django.db.models import Avg
        
        # Get average rating from OrderReview for completed orders
        order_ids = completed_orders.values_list('id', flat=True)
        avg_rating_result = OrderReview.objects.filter(
            order_id__in=order_ids
        ).aggregate(avg_rating=Avg('rating'))
        avg_rating = float(avg_rating_result['avg_rating'] or 0)
        
        # Calculate revision rate (orders with revisions)
        # Check OrderTransitionLog to see if order has ever been in a revision status
        from orders.models import OrderTransitionLog
        revision_statuses = [
            OrderStatus.REVISED.value,
            OrderStatus.IN_REVISION.value,
            OrderStatus.ON_REVISION.value,
            OrderStatus.REVISION_REQUESTED.value,
        ]
        # Get order IDs that have transitions involving revision statuses
        order_ids_list = list(order_ids)
        revised_order_ids_from_transitions = set(
            OrderTransitionLog.objects.filter(
                order_id__in=order_ids_list,
                new_status__in=revision_statuses
            ).values_list('order_id', flat=True).distinct()
        )
        # Also include orders with current status REVISED
        current_revised_ids = set(
            completed_orders.filter(status=OrderStatus.REVISED.value).values_list('id', flat=True)
        )
        # Union both sets to get all revised orders
        all_revised_order_ids = revised_order_ids_from_transitions | current_revised_ids
        revised_orders = len(all_revised_order_ids)
        revision_rate = (revised_orders / completed_orders.count() * 100) if completed_orders.count() > 0 else 0
        
        # Calculate lateness rate (orders submitted late)
        from django.db.models import F
        late_orders = completed_orders.filter(submitted_at__gt=F('deadline')).count()
        lateness_rate = (late_orders / completed_orders.count() * 100) if completed_orders.count() > 0 else 0
        
        return {
            'total_completed_orders': writer.completed_orders or completed_orders.count(),
            'total_takes': writer.number_of_takes or 0,
            'avg_rating': float(avg_rating),
            'completion_rate': float(completion_rate),
            'revision_rate': float(revision_rate),
            'lateness_rate': float(lateness_rate),
        }
    
    @staticmethod
    def get_next_level_requirements(writer):
        """
        Get requirements for the next level the writer can achieve.
        
        Args:
            writer: WriterProfile instance
            
        Returns:
            dict with next level info and requirements
        """
        if not writer.writer_level:
            # Writer has no level, find entry level
            from writer_management.models.levels import WriterLevel
            entry_level = WriterLevel.objects.filter(
                website=writer.website,
                is_active=True,
                min_orders_to_attain=0,
                min_rating_to_attain=0,
                min_takes_to_attain=0
            ).order_by('display_order').first()
            
            if entry_level:
                return {
                    'next_level': entry_level,
                    'requirements': {
                        'min_orders': entry_level.min_orders_to_attain,
                        'min_rating': float(entry_level.min_rating_to_attain),
                        'min_takes': entry_level.min_takes_to_attain,
                        'min_completion_rate': float(entry_level.min_completion_rate),
                    }
                }
            return None
        
        # Find next level (higher display_order means lower level, so we want lower display_order)
        from writer_management.models.levels import WriterLevel
        current_level = writer.writer_level
        next_levels = WriterLevel.objects.filter(
            website=writer.website,
            is_active=True,
            display_order__lt=current_level.display_order
        ).order_by('-display_order')  # Highest level first
        
        for level in next_levels:
            is_eligible, failed = WriterLevelProgressionService.check_level_eligibility(writer, level)
            if is_eligible:
                return {
                    'next_level': level,
                    'is_eligible': True,
                    'requirements': {
                        'min_orders': level.min_orders_to_attain,
                        'min_rating': float(level.min_rating_to_attain),
                        'min_takes': level.min_takes_to_attain,
                        'min_completion_rate': float(level.min_completion_rate),
                    }
                }
            else:
                # Return first next level they're not eligible for (the one they should work towards)
                return {
                    'next_level': level,
                    'is_eligible': False,
                    'failed_requirements': failed,
                    'requirements': {
                        'min_orders': level.min_orders_to_attain,
                        'min_rating': float(level.min_rating_to_attain),
                        'min_takes': level.min_takes_to_attain,
                        'min_completion_rate': float(level.min_completion_rate),
                    }
                }
        
        return None

