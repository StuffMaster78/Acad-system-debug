"""
Feedback System ViewSets
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Avg

from writer_management.models.feedback import Feedback, FeedbackHistory
from writer_management.serializers.feedback import (
    FeedbackSerializer,
    FeedbackCreateSerializer,
    FeedbackHistorySerializer,
)


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing feedback.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = FeedbackSerializer
    
    def get_queryset(self):
        """Get feedback based on user role."""
        user = self.request.user
        website = user.website
        
        if user.role == 'client':
            # Clients see feedback they gave
            queryset = Feedback.objects.filter(
                from_user=user,
                website=website
            )
        elif user.role in ['writer', 'editor']:
            # Writers/editors see feedback they received
            queryset = Feedback.objects.filter(
                to_user=user,
                website=website
            )
        else:
            # Admins see all
            queryset = Feedback.objects.filter(website=website)
        
        # Filter by feedback type
        feedback_type = self.request.query_params.get('feedback_type')
        if feedback_type:
            queryset = queryset.filter(feedback_type=feedback_type)
        
        # Filter by order
        order_id = self.request.query_params.get('order')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        # Filter by rating
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(overall_rating__gte=min_rating)
        
        return queryset.select_related(
            'order', 'from_user', 'to_user', 'website'
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return FeedbackCreateSerializer
        return FeedbackSerializer
    
    def perform_create(self, serializer):
        """Create feedback and recalculate history."""
        feedback = serializer.save(
            from_user=self.request.user,
            website=self.request.user.website
        )
        
        # Recalculate feedback history
        try:
            history = FeedbackHistory.objects.get(
                user=feedback.to_user,
                website=feedback.website
            )
            history.recalculate()
        except FeedbackHistory.DoesNotExist:
            FeedbackHistory.objects.create(
                user=feedback.to_user,
                website=feedback.website
            ).recalculate()
    
    @action(detail=False, methods=['get'], url_path='received')
    def received_feedback(self, request):
        """Get feedback received by current user."""
        queryset = self.get_queryset().filter(to_user=request.user)
        
        # Calculate statistics
        stats = queryset.aggregate(
            total=queryset.count(),
            avg_rating=Avg('overall_rating'),
            avg_quality=Avg('quality_rating'),
            avg_communication=Avg('communication_rating'),
            avg_timeliness=Avg('timeliness_rating'),
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'results': serializer.data,
                'statistics': stats,
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'statistics': stats,
        })
    
    @action(detail=False, methods=['get'], url_path='given')
    def given_feedback(self, request):
        """Get feedback given by current user."""
        queryset = self.get_queryset().filter(from_user=request.user)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FeedbackHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing feedback history (read-only).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = FeedbackHistorySerializer
    
    def get_queryset(self):
        """Get feedback history."""
        user = self.request.user
        website = user.website
        
        if user.role in ['writer', 'editor']:
            # Writers/editors see their own history
            return FeedbackHistory.objects.filter(
                user=user,
                website=website
            )
        elif user.role == 'client':
            # Clients can view writer/editor history (for portfolio)
            target_user_id = self.request.query_params.get('user_id')
            if target_user_id:
                return FeedbackHistory.objects.filter(
                    user_id=target_user_id,
                    website=website
                )
            return FeedbackHistory.objects.none()
        else:
            # Admins see all
            return FeedbackHistory.objects.filter(website=website)
    
    @action(detail=False, methods=['get'], url_path='my-history')
    def my_history(self, request):
        """Get current user's feedback history."""
        try:
            history = FeedbackHistory.objects.get(
                user=request.user,
                website=request.user.website
            )
            serializer = self.get_serializer(history)
            return Response(serializer.data)
        except FeedbackHistory.DoesNotExist:
            return Response({
                'total_feedbacks': 0,
                'average_rating': 0,
                'editor_feedbacks_count': 0,
                'client_feedbacks_count': 0,
            })

