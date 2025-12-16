"""
Assignment Analytics ViewSet

Provides API endpoints for assignment analytics and metrics.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from orders.services.assignment_analytics_service import AssignmentAnalyticsService


class AssignmentAnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for assignment analytics endpoints.
    """
    permission_classes = [IsAuthenticated]
    
    def get_website(self, request):
        """Get website from request (header or query param)."""
        website_id = request.META.get('HTTP_X_WEBSITE') or request.query_params.get('website_id')
        if website_id:
            from websites.models import Website
            try:
                return Website.objects.get(id=website_id)
            except Website.DoesNotExist:
                return None
        return None
    
    def get_date_range(self, request):
        """Get date range from query params."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Default to last 30 days if not specified
        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        else:
            from django.utils.dateparse import parse_date
            start_date = parse_date(start_date)
        
        if not end_date:
            end_date = timezone.now()
        else:
            from django.utils.dateparse import parse_date
            end_date = parse_date(end_date)
        
        return start_date, end_date
    
    @action(detail=False, methods=['get'], url_path='success-rates')
    def success_rates(self, request):
        """
        Get assignment success rates.
        
        Query params:
        - website_id: Filter by website
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        """
        website = self.get_website(request)
        start_date, end_date = self.get_date_range(request)
        
        data = AssignmentAnalyticsService.get_assignment_success_rates(
            website=website,
            start_date=start_date,
            end_date=end_date,
        )
        
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='acceptance-times')
    def acceptance_times(self, request):
        """
        Get average acceptance times.
        
        Query params:
        - website_id: Filter by website
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        """
        website = self.get_website(request)
        start_date, end_date = self.get_date_range(request)
        
        data = AssignmentAnalyticsService.get_average_acceptance_time(
            website=website,
            start_date=start_date,
            end_date=end_date,
        )
        
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='rejection-reasons')
    def rejection_reasons(self, request):
        """
        Get rejection reasons and frequencies.
        
        Query params:
        - website_id: Filter by website
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - limit: Number of top reasons to return (default: 10)
        """
        website = self.get_website(request)
        start_date, end_date = self.get_date_range(request)
        limit = int(request.query_params.get('limit', 10))
        
        data = AssignmentAnalyticsService.get_rejection_reasons(
            website=website,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
        
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='writer-performance')
    def writer_performance(self, request):
        """
        Get writer performance metrics.
        
        Query params:
        - writer_id: Specific writer (optional)
        - website_id: Filter by website
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        """
        website = self.get_website(request)
        start_date, end_date = self.get_date_range(request)
        writer_id = request.query_params.get('writer_id')
        
        if writer_id:
            try:
                writer_id = int(writer_id)
            except ValueError:
                return Response(
                    {"detail": "Invalid writer_id"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        data = AssignmentAnalyticsService.get_writer_performance_metrics(
            writer_id=writer_id,
            website=website,
            start_date=start_date,
            end_date=end_date,
        )
        
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='trends')
    def trends(self, request):
        """
        Get assignment trends over time.
        
        Query params:
        - website_id: Filter by website
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - group_by: 'day', 'week', or 'month' (default: 'day')
        """
        website = self.get_website(request)
        start_date, end_date = self.get_date_range(request)
        group_by = request.query_params.get('group_by', 'day')
        
        if group_by not in ['day', 'week', 'month']:
            return Response(
                {"detail": "group_by must be 'day', 'week', or 'month'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = AssignmentAnalyticsService.get_assignment_trends(
            website=website,
            start_date=start_date,
            end_date=end_date,
            group_by=group_by,
        )
        
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """
        Get comprehensive assignment analytics dashboard.
        
        Query params:
        - website_id: Filter by website
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        """
        website = self.get_website(request)
        start_date, end_date = self.get_date_range(request)
        
        data = AssignmentAnalyticsService.get_comprehensive_dashboard(
            website=website,
            start_date=start_date,
            end_date=end_date,
        )
        
        return Response(data, status=status.HTTP_200_OK)

