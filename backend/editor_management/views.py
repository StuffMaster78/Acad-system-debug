from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.db.models.functions import TruncWeek
from django.utils.timezone import now
from datetime import timedelta

from .models import (
    EditorProfile,
    EditorTaskAssignment,
    EditorReviewSubmission,
    EditorPerformance,
    EditorNotification,
    EditorActionLog,
)
from .serializers import (
    EditorProfileSerializer,
    EditorTaskAssignmentSerializer,
    EditorReviewSubmissionSerializer,
    EditorPerformanceSerializer,
    EditorNotificationSerializer,
    EditorActionLogSerializer,
    ClaimOrderSerializer,
    StartReviewSerializer,
    SubmitReviewSerializer,
    CompleteTaskSerializer,
    RejectTaskSerializer,
    UnclaimTaskSerializer,
)
from .permissions import IsEditor
from .services.editor_assignment_service import EditorAssignmentService
from .services.editor_review_service import EditorReviewService
from orders.models import Order
from orders.order_enums import OrderStatus
from authentication.permissions import IsAdminOrSuperAdmin


class EditorProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for editor profiles.
    """
    queryset = EditorProfile.objects.select_related('user', 'website').prefetch_related(
        'writers_assigned',
        'expertise_subjects',
        'expertise_paper_types'
    )
    serializer_class = EditorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        if user.role == 'editor':
            return self.queryset.filter(user=user)
        elif user.role in ['admin', 'superadmin']:
            return self.queryset.all()
        return self.queryset.none()
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """Get current editor's profile."""
        if request.user.role != 'editor':
            return Response(
                {"detail": "Only editors can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            profile = request.user.editor_profile
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except EditorProfile.DoesNotExist:
            return Response(
                {"detail": "Editor profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get comprehensive dashboard statistics for current editor."""
        if request.user.role != 'editor':
            return Response(
                {"detail": "Only editors can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            profile = request.user.editor_profile
        except EditorProfile.DoesNotExist:
            return Response(
                {"detail": "Editor profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get days parameter (default 30)
        days = int(request.query_params.get('days', 30))
        
        # Use dashboard service
        from editor_management.services.dashboard_service import EditorDashboardService
        dashboard_data = EditorDashboardService.get_dashboard_data(profile, days=days)
        
        return Response(dashboard_data)
    
    @action(detail=False, methods=['get'], url_path='dashboard/tasks')
    def dashboard_tasks(self, request):
        """Get recent and active tasks for editor dashboard."""
        if request.user.role != 'editor':
            return Response(
                {"detail": "Only editors can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            profile = request.user.editor_profile
        except EditorProfile.DoesNotExist:
            return Response(
                {"detail": "Editor profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get query parameters
        limit = int(request.query_params.get('limit', 20))
        status_filter = request.query_params.get('status', None)
        
        # Get tasks
        tasks = EditorTaskAssignment.objects.filter(
            assigned_editor=profile
        ).select_related('order', 'assigned_by').order_by('-assigned_at')
        
        # Filter by status if provided
        if status_filter:
            tasks = tasks.filter(review_status=status_filter)
        
        # Limit results
        tasks = tasks[:limit]
        
        serializer = EditorTaskAssignmentSerializer(tasks, many=True)
        return Response({
            'tasks': serializer.data,
            'count': len(serializer.data),
            'total_active': EditorTaskAssignment.objects.filter(
                assigned_editor=profile,
                review_status__in=['pending', 'in_review']
            ).count()
        })
    
    @action(detail=False, methods=['get'], url_path='dashboard/performance')
    def dashboard_performance(self, request):
        """Get performance analytics for editor dashboard."""
        if request.user.role != 'editor':
            return Response(
                {"detail": "Only editors can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            profile = request.user.editor_profile
        except EditorProfile.DoesNotExist:
            return Response(
                {"detail": "Editor profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        days = int(request.query_params.get('days', 30))
        date_from = now() - timedelta(days=days)
        
        # Get performance data
        from editor_management.services.performance_calculation_service import (
            EditorPerformanceCalculationService
        )
        
        # Calculate/update performance
        performance = EditorPerformanceCalculationService.calculate_performance(profile)
        
        # Get performance stats
        stats = EditorPerformanceCalculationService.get_performance_stats(profile, days=days)
        
        # Get performance trends
        tasks = EditorTaskAssignment.objects.filter(
            assigned_editor=profile,
            reviewed_at__gte=date_from
        )
        
        # Calculate trends by week
        trends = tasks.annotate(
            week=TruncWeek('reviewed_at')
        ).values('week').annotate(
            completed=Count('id', filter=Q(review_status='completed')),
            avg_quality=Avg('review_submission__quality_score')
        ).order_by('week')
        
        return Response({
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
            },
            'stats': stats,
            'trends': [
                {
                    'week': item['week'].isoformat() if item['week'] else None,
                    'completed': item['completed'],
                    'avg_quality_score': float(item['avg_quality']) if item['avg_quality'] else None,
                }
                for item in trends
            ]
        })
    
    @action(detail=False, methods=['get'], url_path='dashboard/analytics')
    def dashboard_analytics(self, request):
        """Get task analytics for editor dashboard."""
        if request.user.role != 'editor':
            return Response(
                {"detail": "Only editors can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            profile = request.user.editor_profile
        except EditorProfile.DoesNotExist:
            return Response(
                {"detail": "Editor profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        days = int(request.query_params.get('days', 30))
        date_from = now() - timedelta(days=days)
        
        # Get all tasks
        all_tasks = EditorTaskAssignment.objects.filter(
            assigned_editor=profile,
            assigned_at__gte=date_from
        )
        
        # Task breakdown by status
        status_breakdown = all_tasks.values('review_status').annotate(
            count=Count('id')
        )
        
        # Task breakdown by assignment type
        assignment_breakdown = all_tasks.values('assignment_type').annotate(
            count=Count('id')
        )
        
        # Tasks by week
        weekly_tasks = all_tasks.annotate(
            week=TruncWeek('assigned_at')
        ).values('week').annotate(
            count=Count('id')
        ).order_by('week')
        
        # Urgent and overdue counts
        urgent_tasks = all_tasks.filter(
            review_status__in=['pending', 'in_review'],
            order__deadline__lte=now() + timedelta(days=7),
            order__deadline__gte=now()
        ).count()
        
        overdue_tasks = all_tasks.filter(
            review_status__in=['pending', 'in_review'],
            order__deadline__lt=now()
        ).count()
        
        return Response({
            'status_breakdown': {item['review_status']: item['count'] for item in status_breakdown},
            'assignment_breakdown': {item['assignment_type']: item['count'] for item in assignment_breakdown},
            'weekly_tasks': [
                {
                    'week': item['week'].isoformat() if item['week'] else None,
                    'count': item['count']
                }
                for item in weekly_tasks
            ],
            'urgent_tasks_count': urgent_tasks,
            'overdue_tasks_count': overdue_tasks,
            'total_tasks': all_tasks.count(),
        })
    
    @action(detail=False, methods=['get'], url_path='dashboard/activity')
    def dashboard_activity(self, request):
        """Get recent activity for editor dashboard."""
        if request.user.role != 'editor':
            return Response(
                {"detail": "Only editors can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            profile = request.user.editor_profile
        except EditorProfile.DoesNotExist:
            return Response(
                {"detail": "Editor profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        days = int(request.query_params.get('days', 7))
        limit = int(request.query_params.get('limit', 20))
        date_from = now() - timedelta(days=days)
        
        # Get recent activity logs
        recent_activity = EditorActionLog.objects.filter(
            editor=profile,
            timestamp__gte=date_from
        ).select_related('related_order').order_by('-timestamp')[:limit]
        
        # Get recent reviews
        recent_reviews = EditorReviewSubmission.objects.filter(
            editor=profile,
            submitted_at__gte=date_from
        ).select_related('order', 'task_assignment').order_by('-submitted_at')[:limit]
        
        # Get recent task assignments
        recent_assignments = EditorTaskAssignment.objects.filter(
            assigned_editor=profile,
            assigned_at__gte=date_from
        ).select_related('order', 'assigned_by').order_by('-assigned_at')[:limit]
        
        return Response({
            'activity_logs': [
                {
                    'id': activity.id,
                    'action_type': activity.action_type,
                    'action': activity.action,
                    'order_id': activity.related_order.id if activity.related_order else None,
                    'order_topic': activity.related_order.topic if activity.related_order else None,
                    'timestamp': activity.timestamp.isoformat() if activity.timestamp else None,
                }
                for activity in recent_activity
            ],
            'recent_reviews': [
                {
                    'id': review.id,
                    'order_id': review.order.id if review.order else None,
                    'order_topic': review.order.topic if review.order else None,
                    'quality_score': float(review.quality_score) if review.quality_score else None,
                    'is_approved': review.is_approved,
                    'requires_revision': review.requires_revision,
                    'submitted_at': review.submitted_at.isoformat() if review.submitted_at else None,
                }
                for review in recent_reviews
            ],
            'recent_assignments': [
                {
                    'id': assignment.id,
                    'order_id': assignment.order.id if assignment.order else None,
                    'order_topic': assignment.order.topic if assignment.order else None,
                    'review_status': assignment.review_status,
                    'assignment_type': assignment.assignment_type,
                    'assigned_at': assignment.assigned_at.isoformat() if assignment.assigned_at else None,
                }
                for assignment in recent_assignments
            ]
        })
    
    @action(detail=False, methods=['get'], url_path='dashboard/workload')
    def dashboard_workload(self, request):
        """Get workload management information for editor dashboard."""
        if request.user.role != 'editor':
            return Response(
                {"detail": "Only editors can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            profile = request.user.editor_profile
        except EditorProfile.DoesNotExist:
            return Response(
                {"detail": "Editor profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get current active tasks
        active_tasks = EditorTaskAssignment.objects.filter(
            assigned_editor=profile,
            review_status__in=['pending', 'in_review']
        ).select_related('order')
        
        # Get max concurrent tasks from profile (if exists)
        max_concurrent = getattr(profile, 'max_concurrent_tasks', 5)  # Default to 5
        
        # Calculate current workload
        current_count = active_tasks.count()
        capacity_percentage = (current_count / max_concurrent * 100) if max_concurrent > 0 else 0
        
        # Get tasks by deadline
        urgent_tasks = active_tasks.filter(
            order__deadline__lte=now() + timedelta(days=1),
            order__deadline__gte=now()
        ).count()
        
        overdue_tasks = active_tasks.filter(
            order__deadline__lt=now()
        ).count()
        
        # Calculate estimated completion times
        tasks_with_deadlines = active_tasks.filter(order__deadline__isnull=False)
        estimated_hours = 0
        for task in tasks_with_deadlines:
            if task.order.deadline:
                hours_until_deadline = (task.order.deadline - now()).total_seconds() / 3600
                estimated_hours += max(0, hours_until_deadline)
        
        # Get recommended order limits
        can_take_more = current_count < max_concurrent
        recommended_limit = max(0, max_concurrent - current_count)
        
        return Response({
            'current_workload': {
                'active_tasks_count': current_count,
                'max_concurrent_tasks': max_concurrent,
                'capacity_percentage': round(capacity_percentage, 2),
                'available_slots': recommended_limit,
                'is_at_capacity': current_count >= max_concurrent,
                'can_take_more': can_take_more,
            },
            'deadline_analysis': {
                'urgent_tasks': urgent_tasks,  # Due within 24 hours
                'overdue_tasks': overdue_tasks,
                'total_with_deadlines': tasks_with_deadlines.count(),
            },
            'time_estimates': {
                'estimated_hours_until_all_deadlines': round(estimated_hours, 2),
                'average_hours_per_task': round(estimated_hours / current_count, 2) if current_count > 0 else 0,
            },
            'recommendations': {
                'recommended_max_orders': recommended_limit,
                'should_claim_more': can_take_more and overdue_tasks == 0,
                'should_focus_on_urgent': urgent_tasks > 0 or overdue_tasks > 0,
            }
        })


class EditorTaskAssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for editor task assignments.
    """
    queryset = EditorTaskAssignment.objects.select_related(
        'order', 'assigned_editor', 'assigned_by'
    ).prefetch_related('fallback_editors')
    serializer_class = EditorTaskAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        
        if user.role == 'editor':
            profile = getattr(user, 'editor_profile', None)
            if not profile:
                return self.queryset.none()
            return self.queryset.filter(assigned_editor=profile)
        elif user.role in ['admin', 'superadmin']:
            return self.queryset.all()
        return self.queryset.none()
    
    @action(detail=False, methods=['get'])
    def available_tasks(self, request):
        """Get available tasks that can be claimed with enhanced filtering."""
        if request.user.role != 'editor':
            return Response(
                {"detail": "Only editors can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            profile = request.user.editor_profile
        except EditorProfile.DoesNotExist:
            return Response(
                {"detail": "Editor profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get query parameters for filtering
        deadline_filter = request.query_params.get('deadline', None)  # 'urgent', 'upcoming', 'all'
        pages_min = request.query_params.get('pages_min', None)
        pages_max = request.query_params.get('pages_max', None)
        paper_type = request.query_params.get('paper_type', None)
        subject = request.query_params.get('subject', None)
        sort_by = request.query_params.get('sort_by', 'deadline')  # 'deadline', 'pages', 'assigned_at'
        limit = int(request.query_params.get('limit', 50))
        
        # Base queryset
        available = self.queryset.filter(
            Q(review_status='unclaimed') | 
            (Q(review_status='pending') & Q(assigned_editor__isnull=True))
        ).filter(
            order__website=profile.website,
            order__status=OrderStatus.UNDER_EDITING.value
        ).select_related('order', 'order__client', 'order__writer')
        
        # Filter by deadline
        if deadline_filter == 'urgent':
            # Due within 24 hours
            available = available.filter(
                order__deadline__lte=now() + timedelta(days=1),
                order__deadline__gte=now()
            )
        elif deadline_filter == 'upcoming':
            # Due within 7 days
            available = available.filter(
                order__deadline__lte=now() + timedelta(days=7),
                order__deadline__gte=now()
            )
        elif deadline_filter == 'overdue':
            # Past deadline
            available = available.filter(order__deadline__lt=now())
        
        # Filter by pages
        if pages_min:
            available = available.filter(order__pages__gte=int(pages_min))
        if pages_max:
            available = available.filter(order__pages__lte=int(pages_max))
        
        # Filter by paper type
        if paper_type:
            available = available.filter(order__paper_type=paper_type)
        
        # Filter by subject
        if subject:
            available = available.filter(order__subject=subject)
        
        # Sort
        if sort_by == 'deadline':
            available = available.order_by('order__deadline')
        elif sort_by == 'pages':
            available = available.order_by('order__pages')
        elif sort_by == 'assigned_at':
            available = available.order_by('-assigned_at')
        else:
            available = available.order_by('order__deadline')
        
        # Limit results
        available = available[:limit]
        
        serializer = self.get_serializer(available, many=True)
        
        # Get summary stats
        total_available = self.queryset.filter(
            Q(review_status='unclaimed') | 
            (Q(review_status='pending') & Q(assigned_editor__isnull=True))
        ).filter(
            order__website=profile.website,
            order__status=OrderStatus.UNDER_EDITING.value
        ).count()
        
        return Response({
            'tasks': serializer.data,
            'count': len(serializer.data),
            'total_available': total_available,
            'filters_applied': {
                'deadline': deadline_filter,
                'pages_min': pages_min,
                'pages_max': pages_max,
                'paper_type': paper_type,
                'subject': subject,
                'sort_by': sort_by,
            }
        })
    
    @action(detail=False, methods=['post'])
    def claim(self, request):
        """Claim an available order."""
        if request.user.role != 'editor':
            return Response(
                {"detail": "Only editors can claim tasks."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ClaimOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            profile = request.user.editor_profile
        except EditorProfile.DoesNotExist:
            return Response(
                {"detail": "Editor profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        order = get_object_or_404(Order, id=serializer.validated_data['order_id'])
        
        try:
            assignment = EditorAssignmentService.claim_order(order, profile)
            serializer = self.get_serializer(assignment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def start_review(self, request, pk=None):
        """Start reviewing a task."""
        if request.user.role != 'editor':
            return Response(
                {"detail": "Only editors can start reviews."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        task = self.get_object()
        
        try:
            profile = request.user.editor_profile
            EditorReviewService.start_review(task, profile)
            serializer = self.get_serializer(task)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def submit_review(self, request):
        """Submit a review for a task."""
        if request.user.role != 'editor':
            return Response(
                {"detail": "Only editors can submit reviews."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = SubmitReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            profile = request.user.editor_profile
        except EditorProfile.DoesNotExist:
            return Response(
                {"detail": "Editor profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        task = get_object_or_404(
            EditorTaskAssignment,
            id=serializer.validated_data['task_id'],
            assigned_editor=profile
        )
        
        try:
            review = EditorReviewService.submit_review(
                task_assignment=task,
                editor=profile,
                **serializer.validated_data
            )
            review_serializer = EditorReviewSubmissionSerializer(review)
            return Response(review_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def complete_task(self, request):
        """Complete a task."""
        if request.user.role != 'editor':
            return Response(
                {"detail": "Only editors can complete tasks."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CompleteTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            profile = request.user.editor_profile
        except EditorProfile.DoesNotExist:
            return Response(
                {"detail": "Editor profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        task = get_object_or_404(
            EditorTaskAssignment,
            id=serializer.validated_data['task_id'],
            assigned_editor=profile
        )
        
        try:
            EditorReviewService.complete_task(
                task,
                profile,
                serializer.validated_data.get('final_notes', '')
            )
            serializer = self.get_serializer(task)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def reject_task(self, request):
        """Reject a task."""
        if request.user.role != 'editor':
            return Response(
                {"detail": "Only editors can reject tasks."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = RejectTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            profile = request.user.editor_profile
        except EditorProfile.DoesNotExist:
            return Response(
                {"detail": "Editor profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        task = get_object_or_404(
            EditorTaskAssignment,
            id=serializer.validated_data['task_id'],
            assigned_editor=profile
        )
        
        try:
            EditorReviewService.reject_task(
                task,
                profile,
                serializer.validated_data['reason']
            )
            serializer = self.get_serializer(task)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def unclaim(self, request):
        """Unclaim a task."""
        if request.user.role != 'editor':
            return Response(
                {"detail": "Only editors can unclaim tasks."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UnclaimTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            profile = request.user.editor_profile
        except EditorProfile.DoesNotExist:
            return Response(
                {"detail": "Editor profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        task = get_object_or_404(
            EditorTaskAssignment,
            id=serializer.validated_data['task_id']
        )
        
        try:
            EditorAssignmentService.unclaim_order(task, profile)
            serializer = self.get_serializer(task)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class EditorReviewSubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for editor review submissions (read-only for viewing past reviews).
    """
    queryset = EditorReviewSubmission.objects.select_related(
        'editor', 'order', 'task_assignment'
    )
    serializer_class = EditorReviewSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        
        if user.role == 'editor':
            profile = getattr(user, 'editor_profile', None)
            if not profile:
                return self.queryset.none()
            return self.queryset.filter(editor=profile)
        elif user.role in ['admin', 'superadmin']:
            return self.queryset.all()
        return self.queryset.none()


class EditorPerformanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving editor performance details.
    """
    queryset = EditorPerformance.objects.select_related('editor')
    serializer_class = EditorPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsEditor]

    def get_queryset(self):
        """Filter to current editor's performance."""
        if self.request.user.role == 'editor':
            try:
                profile = self.request.user.editor_profile
                return self.queryset.filter(editor=profile)
            except EditorProfile.DoesNotExist:
                return self.queryset.none()
        elif self.request.user.role in ['admin', 'superadmin']:
            return self.queryset.all()
        return self.queryset.none()
    
    def list(self, request):
        """Get current editor's performance."""
        if request.user.role != 'editor':
            return Response(
                {"detail": "Only editors can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            profile = request.user.editor_profile
        except EditorProfile.DoesNotExist:
            return Response(
                {"detail": "Editor profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calculate/update performance metrics
        from editor_management.services.performance_calculation_service import (
            EditorPerformanceCalculationService
        )
        performance = EditorPerformanceCalculationService.calculate_performance(profile)
        serializer = self.get_serializer(performance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def detailed_stats(self, request):
        """Get detailed performance statistics."""
        if request.user.role != 'editor':
            return Response(
                {"detail": "Only editors can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            profile = request.user.editor_profile
        except EditorProfile.DoesNotExist:
            return Response(
                {"detail": "Editor profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        days = int(request.query_params.get('days', 30))
        
        from editor_management.services.performance_calculation_service import (
            EditorPerformanceCalculationService
        )
        stats = EditorPerformanceCalculationService.get_performance_stats(profile, days=days)
        
        return Response(stats)


class EditorNotificationsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for editor notifications.
    """
    serializer_class = EditorNotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsEditor]

    def get_queryset(self):
        return EditorNotification.objects.filter(
            editor=self.request.user.editor_profile
        ).select_related('related_order', 'related_task').order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        EditorNotification.objects.filter(
            editor=request.user.editor_profile,
            is_read=False
        ).update(is_read=True)
        return Response({"detail": "All notifications marked as read."})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read."""
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)


# Admin-only ViewSet for manual assignment
class AdminEditorAssignmentViewSet(viewsets.ViewSet):
    """
    Admin-only ViewSet for manually assigning orders to editors.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]
    
    @action(detail=False, methods=['post'])
    def assign(self, request):
        """Manually assign an order to an editor."""
        from .serializers import ManualAssignmentSerializer
        
        serializer = ManualAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order = get_object_or_404(Order, id=serializer.validated_data['order_id'])
        editor = get_object_or_404(
            EditorProfile,
            id=serializer.validated_data['editor_id']
        )
        
        try:
            assignment = EditorAssignmentService.manually_assign_order(
                order=order,
                editor=editor,
                assigned_by=request.user,
                notes=serializer.validated_data.get('notes', '')
            )
            serializer = EditorTaskAssignmentSerializer(assignment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def team_overview(self, request):
        """Get team overview for all editors in a website."""
        from websites.utils import get_current_website
        from editor_management.services.dashboard_service import EditorDashboardService
        
        website = get_current_website(request)
        if not website:
            return Response(
                {"detail": "Website context required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        overview = EditorDashboardService.get_team_overview(website)
        return Response(overview)
    
    @action(detail=False, methods=['get'])
    def rankings(self, request):
        """Get editor performance rankings."""
        from websites.utils import get_current_website
        from editor_management.services.performance_calculation_service import (
            EditorPerformanceCalculationService
        )
        
        website = get_current_website(request)
        limit = int(request.query_params.get('limit', 10))
        
        rankings = EditorPerformanceCalculationService.get_editor_rankings(
            website=website,
            limit=limit
        )
        
        return Response(rankings)
    
    @action(detail=False, methods=['post'])
    def recalculate_performance(self, request):
        """Trigger performance recalculation for all editors or specific editor."""
        from websites.utils import get_current_website
        from editor_management.services.performance_calculation_service import (
            EditorPerformanceCalculationService
        )
        
        editor_id = request.data.get('editor_id')
        
        if editor_id:
            # Recalculate for specific editor
            editor = get_object_or_404(EditorProfile, id=editor_id)
            performance = EditorPerformanceCalculationService.calculate_performance(editor)
            serializer = EditorPerformanceSerializer(performance)
            return Response(serializer.data)
        else:
            # Recalculate for all editors in website
            website = get_current_website(request)
            results = EditorPerformanceCalculationService.calculate_all_editors_performance(
                website=website
            )
            return Response(results)
