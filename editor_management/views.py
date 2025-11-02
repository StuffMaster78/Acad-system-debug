from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
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
        """Get available tasks that can be claimed."""
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
        
        available = self.queryset.filter(
            Q(review_status='unclaimed') | 
            (Q(review_status='pending') & Q(assigned_editor__isnull=True))
        ).filter(
            order__website=profile.website,
            order__status=OrderStatus.UNDER_EDITING.value
        )
        
        serializer = self.get_serializer(available, many=True)
        return Response(serializer.data)
    
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
