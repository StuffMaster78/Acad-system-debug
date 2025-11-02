"""
Service for calculating and updating editor performance metrics.
"""

from django.db.models import Avg, Count, Sum, F, DurationField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from datetime import timedelta
from typing import Dict, Optional

from editor_management.models import (
    EditorProfile,
    EditorPerformance,
    EditorTaskAssignment,
    EditorReviewSubmission
)
from orders.models import Order
from orders.order_enums import OrderStatus


class EditorPerformanceCalculationService:
    """
    Calculates and updates editor performance metrics.
    """
    
    @staticmethod
    def calculate_performance(editor: EditorProfile) -> EditorPerformance:
        """
        Calculate performance metrics for an editor.
        
        Args:
            editor: The editor profile
            
        Returns:
            EditorPerformance instance with updated metrics
        """
        performance, created = EditorPerformance.objects.get_or_create(
            editor=editor,
            defaults={
                'total_orders_reviewed': 0,
                'late_reviews': 0,
            }
        )
        
        # Calculate average review time
        completed_tasks = EditorTaskAssignment.objects.filter(
            assigned_editor=editor,
            review_status='completed',
            started_at__isnull=False,
            reviewed_at__isnull=False
        )
        
        if completed_tasks.exists():
            # Calculate average time difference
            avg_time = completed_tasks.annotate(
                review_duration=ExpressionWrapper(
                    F('reviewed_at') - F('started_at'),
                    output_field=DurationField()
                )
            ).aggregate(
                avg_duration=Avg('review_duration')
            )['avg_duration']
            
            performance.average_review_time = avg_time
        
        # Update total orders reviewed (should match editor.orders_reviewed)
        performance.total_orders_reviewed = editor.orders_reviewed
        
        # Calculate late reviews (reviews completed after order deadline)
        late_reviews_count = EditorTaskAssignment.objects.filter(
            assigned_editor=editor,
            review_status='completed',
            reviewed_at__isnull=False
        ).filter(
            reviewed_at__gt=F('order__deadline')
        ).count()
        
        performance.late_reviews = late_reviews_count
        
        # Calculate average quality score (from admin ratings)
        if editor.assigned_tasks.filter(editor_rating__isnull=False).exists():
            avg_rating = editor.assigned_tasks.filter(
                editor_rating__isnull=False
            ).aggregate(
                avg=Avg('editor_rating')
            )['avg']
            performance.average_quality_score = avg_rating
        
        # Calculate revisions requested count
        revisions_count = EditorReviewSubmission.objects.filter(
            editor=editor,
            requires_revision=True
        ).count()
        performance.revisions_requested_count = revisions_count
        
        # Calculate approvals count
        approvals_count = EditorReviewSubmission.objects.filter(
            editor=editor,
            is_approved=True
        ).count()
        performance.approvals_count = approvals_count
        
        # Update last calculated timestamp
        performance.last_calculated_at = now()
        performance.save()
        
        return performance
    
    @staticmethod
    def calculate_all_editors_performance(website=None) -> Dict[str, int]:
        """
        Calculate performance for all editors (or editors in a website).
        
        Args:
            website: Optional website to filter editors
            
        Returns:
            Dict with calculation results
        """
        editors = EditorProfile.objects.filter(is_active=True)
        if website:
            editors = editors.filter(website=website)
        
        calculated = 0
        failed = 0
        
        for editor in editors:
            try:
                EditorPerformanceCalculationService.calculate_performance(editor)
                calculated += 1
            except Exception:
                failed += 1
        
        return {
            'calculated': calculated,
            'failed': failed,
            'total': editors.count()
        }
    
    @staticmethod
    def get_performance_stats(editor: EditorProfile, days: int = 30) -> Dict:
        """
        Get detailed performance statistics for an editor over a period.
        
        Args:
            editor: The editor profile
            days: Number of days to look back
            
        Returns:
            Dict with performance statistics
        """
        cutoff_date = now() - timedelta(days=days)
        
        # Recent tasks
        recent_tasks = EditorTaskAssignment.objects.filter(
            assigned_editor=editor,
            assigned_at__gte=cutoff_date
        )
        
        # Completed tasks
        completed_tasks = recent_tasks.filter(review_status='completed')
        
        # In-progress tasks
        active_tasks = recent_tasks.filter(
            review_status__in=['pending', 'in_review']
        )
        
        # Calculate average completion time for recent tasks
        completed_with_times = completed_tasks.filter(
            started_at__isnull=False,
            reviewed_at__isnull=False
        )
        
        avg_completion_time = None
        if completed_with_times.exists():
            total_seconds = sum(
                (task.reviewed_at - task.started_at).total_seconds()
                for task in completed_with_times
            )
            avg_completion_time = total_seconds / completed_with_times.count()
        
        # Quality scores
        quality_scores = completed_tasks.filter(
            editor_rating__isnull=False
        ).values_list('editor_rating', flat=True)
        
        # Review submissions
        recent_reviews = EditorReviewSubmission.objects.filter(
            editor=editor,
            submitted_at__gte=cutoff_date
        )
        
        approval_rate = None
        if recent_reviews.exists():
            approved = recent_reviews.filter(is_approved=True).count()
            approval_rate = (approved / recent_reviews.count()) * 100
        
        revision_rate = None
        if recent_reviews.exists():
            revisions = recent_reviews.filter(requires_revision=True).count()
            revision_rate = (revisions / recent_reviews.count()) * 100
        
        # Average quality score from reviews
        avg_quality_from_reviews = None
        reviews_with_scores = recent_reviews.filter(quality_score__isnull=False)
        if reviews_with_scores.exists():
            avg_quality_from_reviews = reviews_with_scores.aggregate(
                avg=Avg('quality_score')
            )['avg']
        
        return {
            'period_days': days,
            'total_tasks_assigned': recent_tasks.count(),
            'completed_tasks': completed_tasks.count(),
            'active_tasks': active_tasks.count(),
            'average_completion_time_seconds': avg_completion_time,
            'average_completion_time_hours': avg_completion_time / 3600 if avg_completion_time else None,
            'approval_rate_percent': approval_rate,
            'revision_rate_percent': revision_rate,
            'average_quality_score': avg_quality_from_reviews,
            'admin_ratings_average': sum(quality_scores) / len(quality_scores) if quality_scores else None,
            'total_admin_ratings': len(quality_scores),
            'on_time_completion_rate': None,  # Can be calculated with deadline info
        }
    
    @staticmethod
    def get_editor_rankings(website=None, limit: int = 10) -> list:
        """
        Get ranked list of editors by performance.
        
        Args:
            website: Optional website to filter
            limit: Number of top editors to return
            
        Returns:
            List of editor performance data
        """
        editors = EditorProfile.objects.filter(is_active=True)
        if website:
            editors = editors.filter(website=website)
        
        # Calculate performance for all editors first
        EditorPerformanceCalculationService.calculate_all_editors_performance(website)
        
        # Get editors with their performance
        performances = EditorPerformance.objects.filter(
            editor__in=editors
        ).select_related('editor').order_by(
            '-total_orders_reviewed',
            '-average_quality_score',
            'late_reviews'
        )[:limit]
        
        rankings = []
        for idx, perf in enumerate(performances, 1):
            rankings.append({
                'rank': idx,
                'editor_id': perf.editor.id,
                'editor_name': perf.editor.name,
                'total_reviews': perf.total_orders_reviewed,
                'average_quality_score': float(perf.average_quality_score) if perf.average_quality_score else None,
                'late_reviews': perf.late_reviews,
                'approval_rate': (
                    (perf.approvals_count / perf.total_orders_reviewed * 100)
                    if perf.total_orders_reviewed > 0 else 0
                ),
            })
        
        return rankings

