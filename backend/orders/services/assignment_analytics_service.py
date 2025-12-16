"""
Assignment Analytics Service

Provides analytics and metrics for order assignments including:
- Assignment success rates
- Average time to acceptance
- Rejection reasons
- Writer performance metrics
"""
from typing import Dict, List, Optional
from datetime import timedelta
from django.db.models import Count, Avg, Q, F, ExpressionWrapper, DurationField, Sum
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone
from django.contrib.auth import get_user_model

from orders.models import Order, WriterAssignmentAcceptance, OrderRequest, OrderRequestStatus, OrderStatus
from writer_management.models.profile import WriterProfile

User = get_user_model()


class AssignmentAnalyticsService:
    """
    Service for analyzing assignment metrics and performance.
    """
    
    @staticmethod
    def get_assignment_success_rates(
        website=None,
        start_date=None,
        end_date=None,
    ) -> Dict:
        """
        Get assignment success rates.
        
        Returns:
            Dictionary with success rate metrics
        """
        # Base queryset
        acceptances = WriterAssignmentAcceptance.objects.all()
        
        if website:
            acceptances = acceptances.filter(website=website)
        
        if start_date:
            acceptances = acceptances.filter(assigned_at__gte=start_date)
        if end_date:
            acceptances = acceptances.filter(assigned_at__lte=end_date)
        
        total = acceptances.count()
        accepted = acceptances.filter(status='accepted').count()
        rejected = acceptances.filter(status='rejected').count()
        pending = acceptances.filter(status='pending').count()
        
        success_rate = (accepted / total * 100) if total > 0 else 0
        rejection_rate = (rejected / total * 100) if total > 0 else 0
        pending_rate = (pending / total * 100) if total > 0 else 0
        
        return {
            'total_assignments': total,
            'accepted': accepted,
            'rejected': rejected,
            'pending': pending,
            'success_rate': round(success_rate, 2),
            'rejection_rate': round(rejection_rate, 2),
            'pending_rate': round(pending_rate, 2),
        }
    
    @staticmethod
    def get_average_acceptance_time(
        website=None,
        start_date=None,
        end_date=None,
    ) -> Dict:
        """
        Get average time to acceptance.
        
        Returns:
            Dictionary with acceptance time metrics
        """
        acceptances = WriterAssignmentAcceptance.objects.filter(
            status='accepted',
            responded_at__isnull=False,
        )
        
        if website:
            acceptances = acceptances.filter(website=website)
        
        if start_date:
            acceptances = acceptances.filter(assigned_at__gte=start_date)
        if end_date:
            acceptances = acceptances.filter(assigned_at__lte=end_date)
        
        # Calculate time difference
        acceptances = acceptances.annotate(
            response_time=ExpressionWrapper(
                F('responded_at') - F('assigned_at'),
                output_field=DurationField()
            )
        )
        
        # Get average response time
        avg_response = acceptances.aggregate(
            avg_time=Avg('response_time')
        )['avg_time']
        
        # Get median (approximate)
        response_times = list(acceptances.values_list('response_time', flat=True))
        response_times = [t for t in response_times if t is not None]
        
        median_time = None
        if response_times:
            sorted_times = sorted(response_times)
            n = len(sorted_times)
            if n % 2 == 0:
                median_time = (sorted_times[n//2 - 1] + sorted_times[n//2]) / 2
            else:
                median_time = sorted_times[n//2]
        
        # Convert to hours for readability
        avg_hours = None
        median_hours = None
        
        if avg_response:
            avg_hours = avg_response.total_seconds() / 3600.0
        
        if median_time:
            median_hours = median_time.total_seconds() / 3600.0
        
        # Get distribution by time ranges
        distribution = {
            'under_1_hour': acceptances.filter(
                response_time__lt=timedelta(hours=1)
            ).count(),
            '1_to_6_hours': acceptances.filter(
                response_time__gte=timedelta(hours=1),
                response_time__lt=timedelta(hours=6)
            ).count(),
            '6_to_24_hours': acceptances.filter(
                response_time__gte=timedelta(hours=6),
                response_time__lt=timedelta(hours=24)
            ).count(),
            'over_24_hours': acceptances.filter(
                response_time__gte=timedelta(hours=24)
            ).count(),
        }
        
        return {
            'average_hours': round(avg_hours, 2) if avg_hours else None,
            'median_hours': round(median_hours, 2) if median_hours else None,
            'total_accepted': acceptances.count(),
            'distribution': distribution,
        }
    
    @staticmethod
    def get_rejection_reasons(
        website=None,
        start_date=None,
        end_date=None,
        limit: int = 10,
    ) -> List[Dict]:
        """
        Get rejection reasons and their frequencies.
        
        Returns:
            List of rejection reason dictionaries
        """
        rejections = WriterAssignmentAcceptance.objects.filter(
            status='rejected',
            reason__isnull=False,
        )
        
        if website:
            rejections = rejections.filter(website=website)
        
        if start_date:
            rejections = rejections.filter(assigned_at__gte=start_date)
        if end_date:
            rejections = rejections.filter(assigned_at__lte=end_date)
        
        # Group by reason (simplified - using first 100 chars)
        from collections import Counter
        reasons = []
        
        for rejection in rejections:
            reason = rejection.reason or "No reason provided"
            # Truncate long reasons
            reason_key = reason[:100] if len(reason) > 100 else reason
            reasons.append(reason_key)
        
        reason_counts = Counter(reasons)
        
        # Format results
        result = []
        for reason, count in reason_counts.most_common(limit):
            result.append({
                'reason': reason,
                'count': count,
                'percentage': round((count / len(reasons) * 100) if reasons else 0, 2),
            })
        
        return result
    
    @staticmethod
    def get_writer_performance_metrics(
        writer_id: Optional[int] = None,
        website=None,
        start_date=None,
        end_date=None,
    ) -> Dict:
        """
        Get writer performance metrics for assignments.
        
        Args:
            writer_id: Specific writer ID (optional)
            website: Filter by website
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Dictionary with writer performance metrics
        """
        acceptances = WriterAssignmentAcceptance.objects.all()
        
        if writer_id:
            acceptances = acceptances.filter(writer_id=writer_id)
        if website:
            acceptances = acceptances.filter(website=website)
        if start_date:
            acceptances = acceptances.filter(assigned_at__gte=start_date)
        if end_date:
            acceptances = acceptances.filter(assigned_at__lte=end_date)
        
        # Aggregate by writer
        writer_stats = acceptances.values('writer_id', 'writer__username').annotate(
            total_assignments=Count('id'),
            accepted=Count('id', filter=Q(status='accepted')),
            rejected=Count('id', filter=Q(status='rejected')),
            pending=Count('id', filter=Q(status='pending')),
        ).annotate(
            acceptance_rate=ExpressionWrapper(
                F('accepted') * 100.0 / F('total_assignments'),
                output_field=DurationField()
            ) if F('total_assignments') > 0 else 0
        )
        
        # Calculate average response time per writer
        writer_response_times = {}
        for writer_id_val in acceptances.values_list('writer_id', flat=True).distinct():
            writer_acceptances = acceptances.filter(
                writer_id=writer_id_val,
                status='accepted',
                responded_at__isnull=False,
            ).annotate(
                response_time=ExpressionWrapper(
                    F('responded_at') - F('assigned_at'),
                    output_field=DurationField()
                )
            )
            
            avg_time = writer_acceptances.aggregate(
                avg=Avg('response_time')
            )['avg']
            
            if avg_time:
                writer_response_times[writer_id_val] = avg_time.total_seconds() / 3600.0
        
        # Format results
        results = []
        for stat in writer_stats:
            writer_id_val = stat['writer_id']
            results.append({
                'writer_id': writer_id_val,
                'writer_username': stat['writer__username'],
                'total_assignments': stat['total_assignments'],
                'accepted': stat['accepted'],
                'rejected': stat['rejected'],
                'pending': stat['pending'],
                'acceptance_rate': round(
                    (stat['accepted'] / stat['total_assignments'] * 100) if stat['total_assignments'] > 0 else 0,
                    2
                ),
                'average_response_hours': round(
                    writer_response_times.get(writer_id_val, 0),
                    2
                ),
            })
        
        # Sort by total assignments (descending)
        results.sort(key=lambda x: x['total_assignments'], reverse=True)
        
        return {
            'writers': results,
            'total_writers': len(results),
        }
    
    @staticmethod
    def get_assignment_trends(
        website=None,
        start_date=None,
        end_date=None,
        group_by: str = 'day',  # 'day', 'week', 'month'
    ) -> List[Dict]:
        """
        Get assignment trends over time.
        
        Args:
            website: Filter by website
            start_date: Start date
            end_date: End date
            group_by: Grouping period ('day', 'week', 'month')
            
        Returns:
            List of trend data points
        """
        acceptances = WriterAssignmentAcceptance.objects.all()
        
        if website:
            acceptances = acceptances.filter(website=website)
        if start_date:
            acceptances = acceptances.filter(assigned_at__gte=start_date)
        if end_date:
            acceptances = acceptances.filter(assigned_at__lte=end_date)
        
        # Group by date
        if group_by == 'day':
            grouped = acceptances.annotate(
                date=TruncDate('assigned_at')
            ).values('date').annotate(
                total=Count('id'),
                accepted=Count('id', filter=Q(status='accepted')),
                rejected=Count('id', filter=Q(status='rejected')),
            ).order_by('date')
        elif group_by == 'week':
            from django.db.models.functions import TruncWeek
            grouped = acceptances.annotate(
                week=TruncWeek('assigned_at')
            ).values('week').annotate(
                total=Count('id'),
                accepted=Count('id', filter=Q(status='accepted')),
                rejected=Count('id', filter=Q(status='rejected')),
            ).order_by('week')
        else:  # month
            from django.db.models.functions import TruncMonth
            grouped = acceptances.annotate(
                month=TruncMonth('assigned_at')
            ).values('month').annotate(
                total=Count('id'),
                accepted=Count('id', filter=Q(status='accepted')),
                rejected=Count('id', filter=Q(status='rejected')),
            ).order_by('month')
        
        results = []
        for item in grouped:
            date_key = 'date' if group_by == 'day' else ('week' if group_by == 'week' else 'month')
            results.append({
                'period': str(item[date_key]),
                'total': item['total'],
                'accepted': item['accepted'],
                'rejected': item['rejected'],
                'success_rate': round(
                    (item['accepted'] / item['total'] * 100) if item['total'] > 0 else 0,
                    2
                ),
            })
        
        return results
    
    @staticmethod
    def get_comprehensive_dashboard(
        website=None,
        start_date=None,
        end_date=None,
    ) -> Dict:
        """
        Get comprehensive assignment analytics dashboard.
        
        Returns:
            Complete dashboard data
        """
        return {
            'success_rates': AssignmentAnalyticsService.get_assignment_success_rates(
                website=website,
                start_date=start_date,
                end_date=end_date,
            ),
            'acceptance_times': AssignmentAnalyticsService.get_average_acceptance_time(
                website=website,
                start_date=start_date,
                end_date=end_date,
            ),
            'rejection_reasons': AssignmentAnalyticsService.get_rejection_reasons(
                website=website,
                start_date=start_date,
                end_date=end_date,
            ),
            'writer_performance': AssignmentAnalyticsService.get_writer_performance_metrics(
                website=website,
                start_date=start_date,
                end_date=end_date,
            ),
            'trends': AssignmentAnalyticsService.get_assignment_trends(
                website=website,
                start_date=start_date,
                end_date=end_date,
            ),
        }

