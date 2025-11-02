"""
Service for generating editor dashboard data.
"""

from django.db.models import Count, Q, Avg, Sum
from django.utils.timezone import now
from datetime import timedelta
from typing import Dict, List, Optional

from editor_management.models import (
    EditorProfile,
    EditorTaskAssignment,
    EditorReviewSubmission,
    EditorPerformance
)
from orders.models import Order
from orders.order_enums import OrderStatus
from editor_management.services.performance_calculation_service import (
    EditorPerformanceCalculationService
)


class EditorDashboardService:
    """
    Service for generating comprehensive dashboard data for editors.
    """
    
    @staticmethod
    def get_dashboard_data(editor: EditorProfile, days: int = 30) -> Dict:
        """
        Get complete dashboard data for an editor.
        
        Args:
            editor: The editor profile
            days: Number of days for statistics
            
        Returns:
            Dict with dashboard data
        """
        cutoff_date = now() - timedelta(days=days)
        
        # Task statistics
        all_tasks = EditorTaskAssignment.objects.filter(assigned_editor=editor)
        active_tasks = all_tasks.filter(review_status__in=['pending', 'in_review'])
        pending_tasks = all_tasks.filter(review_status='pending')
        in_review_tasks = all_tasks.filter(review_status='in_review')
        completed_tasks = all_tasks.filter(review_status='completed')
        
        # Available tasks (unclaimed in editor's website)
        available_tasks = EditorTaskAssignment.objects.filter(
            Q(review_status='unclaimed') | 
            (Q(review_status='pending') & Q(assigned_editor__isnull=True))
        ).filter(
            order__website=editor.website,
            order__status=OrderStatus.UNDER_EDITING.value
        )
        
        # Recent completions
        recent_completions = completed_tasks.filter(
            reviewed_at__gte=cutoff_date
        )
        
        # Upcoming deadlines (tasks due in next 7 days)
        upcoming_deadline = now() + timedelta(days=7)
        urgent_tasks = active_tasks.filter(
            order__deadline__lte=upcoming_deadline,
            order__deadline__gte=now()
        )
        
        # Overdue tasks
        overdue_tasks = active_tasks.filter(
            order__deadline__lt=now()
        )
        
        # Performance metrics
        try:
            performance = editor.performance
        except EditorPerformance.DoesNotExist:
            performance = EditorPerformanceCalculationService.calculate_performance(editor)
        
        # Performance stats
        performance_stats = EditorPerformanceCalculationService.get_performance_stats(
            editor, days=days
        )
        
        # Recent activity
        from editor_management.models import EditorActionLog
        recent_activity = EditorActionLog.objects.filter(
            editor=editor,
            timestamp__gte=cutoff_date
        ).select_related('related_order').order_by('-timestamp')[:10]
        
        # Task breakdown by status
        task_breakdown = {
            'pending': pending_tasks.count(),
            'in_review': in_review_tasks.count(),
            'completed': completed_tasks.count(),
            'rejected': all_tasks.filter(review_status='rejected').count(),
            'unclaimed': all_tasks.filter(review_status='unclaimed').count(),
        }
        
        # Task breakdown by assignment type
        assignment_breakdown = {
            'auto': all_tasks.filter(assignment_type='auto').count(),
            'manual': all_tasks.filter(assignment_type='manual').count(),
            'claimed': all_tasks.filter(assignment_type='claimed').count(),
        }
        
        # Recent reviews
        recent_reviews = EditorReviewSubmission.objects.filter(
            editor=editor,
            submitted_at__gte=cutoff_date
        ).select_related('order', 'task_assignment').order_by('-submitted_at')[:10]
        
        return {
            'summary': {
                'active_tasks_count': active_tasks.count(),
                'pending_tasks_count': pending_tasks.count(),
                'in_review_tasks_count': in_review_tasks.count(),
                'available_tasks_count': available_tasks.count(),
                'recent_completions': recent_completions.count(),
                'urgent_tasks_count': urgent_tasks.count(),
                'overdue_tasks_count': overdue_tasks.count(),
                'can_take_more_tasks': editor.can_take_more_tasks(),
                'max_concurrent_tasks': editor.max_concurrent_tasks,
                'current_workload_percent': (
                    (active_tasks.count() / editor.max_concurrent_tasks * 100)
                    if editor.max_concurrent_tasks > 0 else 0
                ),
            },
            'performance': {
                'total_orders_reviewed': performance.total_orders_reviewed,
                'average_review_time_hours': (
                    performance.average_review_time.total_seconds() / 3600
                    if performance.average_review_time else None
                ),
                'late_reviews': performance.late_reviews,
                'average_quality_score': float(performance.average_quality_score)
                if performance.average_quality_score else None,
                'revisions_requested_count': performance.revisions_requested_count,
                'approvals_count': performance.approvals_count,
                'last_calculated_at': performance.last_calculated_at,
                **performance_stats,
            },
            'tasks': {
                'breakdown_by_status': task_breakdown,
                'breakdown_by_assignment_type': assignment_breakdown,
                'active_tasks': [
                    {
                        'id': task.id,
                        'order_id': task.order.id,
                        'order_topic': task.order.topic,
                        'deadline': task.order.deadline,
                        'status': task.review_status,
                        'assigned_at': task.assigned_at,
                        'started_at': task.started_at,
                    }
                    for task in active_tasks.select_related('order')[:10]
                ],
                'available_tasks': [
                    {
                        'id': task.id if task else None,
                        'order_id': task.order.id if task else None,
                        'order_topic': task.order.topic if task else None,
                        'deadline': task.order.deadline if task else None,
                    }
                    for task in available_tasks.select_related('order')[:10]
                ],
                'urgent_tasks': [
                    {
                        'id': task.id,
                        'order_id': task.order.id,
                        'order_topic': task.order.topic,
                        'deadline': task.order.deadline,
                        'days_until_deadline': (task.order.deadline - now()).days,
                    }
                    for task in urgent_tasks.select_related('order')
                ],
                'overdue_tasks': [
                    {
                        'id': task.id,
                        'order_id': task.order.id,
                        'order_topic': task.order.topic,
                        'deadline': task.order.deadline,
                        'days_overdue': (now() - task.order.deadline).days,
                    }
                    for task in overdue_tasks.select_related('order')
                ],
            },
            'recent_activity': [
                {
                    'action_type': activity.action_type,
                    'action': activity.action,
                    'order_id': activity.related_order.id if activity.related_order else None,
                    'timestamp': activity.timestamp,
                }
                for activity in recent_activity
            ],
            'recent_reviews': [
                {
                    'id': review.id,
                    'order_id': review.order.id,
                    'order_topic': review.order.topic,
                    'quality_score': float(review.quality_score) if review.quality_score else None,
                    'is_approved': review.is_approved,
                    'requires_revision': review.requires_revision,
                    'submitted_at': review.submitted_at,
                }
                for review in recent_reviews
            ],
        }
    
    @staticmethod
    def get_team_overview(website) -> Dict:
        """
        Get team overview for admin (all editors in website).
        
        Args:
            website: Website to get editors for
            
        Returns:
            Dict with team overview data
        """
        editors = EditorProfile.objects.filter(
            website=website,
            is_active=True
        )
        
        # Calculate performance for all editors
        EditorPerformanceCalculationService.calculate_all_editors_performance(website)
        
        # Get all tasks for these editors
        all_tasks = EditorTaskAssignment.objects.filter(
            assigned_editor__in=editors,
            order__website=website
        )
        
        # Unassigned tasks
        unassigned_tasks = EditorTaskAssignment.objects.filter(
            order__website=website,
            order__status=OrderStatus.UNDER_EDITING.value
        ).filter(
            Q(review_status='unclaimed') | 
            (Q(review_status='pending') & Q(assigned_editor__isnull=True))
        )
        
        # Editor stats
        editor_stats = []
        for editor in editors:
            active_count = all_tasks.filter(
                assigned_editor=editor,
                review_status__in=['pending', 'in_review']
            ).count()
            
            try:
                perf = editor.performance
            except EditorPerformance.DoesNotExist:
                perf = EditorPerformanceCalculationService.calculate_performance(editor)
            
            editor_stats.append({
                'editor_id': editor.id,
                'editor_name': editor.name,
                'active_tasks': active_count,
                'max_tasks': editor.max_concurrent_tasks,
                'utilization_percent': (
                    (active_count / editor.max_concurrent_tasks * 100)
                    if editor.max_concurrent_tasks > 0 else 0
                ),
                'total_reviewed': perf.total_orders_reviewed,
                'average_quality_score': float(perf.average_quality_score)
                if perf.average_quality_score else None,
                'can_take_more': editor.can_take_more_tasks(),
            })
        
        return {
            'total_editors': editors.count(),
            'active_editors': editors.filter(
                id__in=all_tasks.filter(
                    review_status__in=['pending', 'in_review']
                ).values_list('assigned_editor_id', flat=True).distinct()
            ).count(),
            'unassigned_tasks': unassigned_tasks.count(),
            'total_active_tasks': all_tasks.filter(
                review_status__in=['pending', 'in_review']
            ).count(),
            'editor_stats': editor_stats,
            'top_performers': EditorPerformanceCalculationService.get_editor_rankings(
                website=website,
                limit=5
            ),
        }

