"""
Performance Metrics Service for Support Management
"""
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
from tickets.models import Ticket, TicketMessage
from orders.models import Dispute
from support_management.models import SupportProfile, OrderDisputeSLA


class SupportPerformanceService:
    """
    Service for calculating and tracking support agent performance metrics.
    """
    
    def __init__(self, support_user, days=30):
        """
        Initialize performance service for a specific support agent.
        
        Args:
            support_user: Support user to analyze
            days: Number of days to analyze (default: 30)
        """
        self.support_user = support_user
        self.days = days
        self.start_date = timezone.now() - timedelta(days=days)
    
    def calculate_performance_score(self):
        """
        Calculate overall performance score (0-100).
        
        Returns:
            float: Performance score
        """
        resolution_rate = self._get_resolution_rate()
        avg_response_time = self._get_avg_response_time()
        sla_compliance = self._get_sla_compliance_rate()
        
        # Normalize response time (assume 24 hours is max acceptable)
        response_score = max(0, 1 - (avg_response_time / 24)) if avg_response_time else 0
        
        # Weighted score
        score = (
            resolution_rate * 0.4 +
            response_score * 0.3 +
            sla_compliance * 0.3
        ) * 100
        
        return round(score, 2)
    
    def get_performance_metrics(self):
        """
        Get comprehensive performance metrics.
        
        Returns:
            dict: All performance metrics
        """
        tickets = Ticket.objects.filter(
            assigned_to=self.support_user,
            created_at__gte=self.start_date
        )
        
        resolved = tickets.filter(status='closed')
        
        return {
            'performance_score': self.calculate_performance_score(),
            'tickets_handled': tickets.count(),
            'tickets_resolved': resolved.count(),
            'resolution_rate': self._get_resolution_rate(),
            'avg_response_time_hours': self._get_avg_response_time(),
            'avg_resolution_time_hours': self._get_avg_resolution_time(),
            'sla_compliance_rate': self._get_sla_compliance_rate(),
            'customer_satisfaction': self._get_customer_satisfaction(),  # Placeholder
            'tickets_resolved_today': self._get_tickets_resolved_today(),
            'tickets_resolved_this_week': self._get_tickets_resolved_this_week(),
            'tickets_resolved_this_month': resolved.count(),
        }
    
    def calculate_and_cache_metrics(self):
        """
        Calculate and cache performance metrics (for daily task).
        """
        metrics = self.get_performance_metrics()
        # Could store in a cache or separate PerformanceMetrics model
        # For now, just return the metrics
        return metrics
    
    def get_performance_trends(self):
        """
        Get performance trends over time.
        
        Returns:
            list: Weekly performance data
        """
        trends = []
        weeks = self.days // 7
        
        for week in range(weeks):
            week_start = self.start_date + timedelta(weeks=week)
            week_end = week_start + timedelta(days=7)
            
            week_tickets = Ticket.objects.filter(
                assigned_to=self.support_user,
                created_at__gte=week_start,
                created_at__lt=week_end
            )
            
            week_resolved = week_tickets.filter(status='closed')
            
            trends.append({
                'week': week + 1,
                'week_start': week_start.date().isoformat(),
                'tickets_handled': week_tickets.count(),
                'tickets_resolved': week_resolved.count(),
                'resolution_rate': (week_resolved.count() / week_tickets.count() * 100) if week_tickets.count() > 0 else 0,
            })
        
        return trends
    
    def _get_resolution_rate(self):
        """Get ticket resolution rate as percentage."""
        tickets = Ticket.objects.filter(
            assigned_to=self.support_user,
            created_at__gte=self.start_date
        )
        
        if tickets.count() == 0:
            return 0
        
        resolved = tickets.filter(status='closed').count()
        return (resolved / tickets.count()) * 100
    
    def _get_avg_response_time(self):
        """Get average first response time in hours."""
        tickets = Ticket.objects.filter(
            assigned_to=self.support_user,
            created_at__gte=self.start_date
        )
        
        response_times = []
        for ticket in tickets:
            first_message = TicketMessage.objects.filter(
                ticket=ticket,
                sender=self.support_user
            ).order_by('created_at').first()
            
            if first_message and ticket.created_at:
                response_time = (first_message.created_at - ticket.created_at).total_seconds() / 3600
                response_times.append(response_time)
        
        return sum(response_times) / len(response_times) if response_times else None
    
    def _get_avg_resolution_time(self):
        """Get average resolution time in hours."""
        resolved = Ticket.objects.filter(
            assigned_to=self.support_user,
            status='closed',
            created_at__gte=self.start_date
        )
        
        if not resolved.exists():
            return None
        
        total_time = 0
        count = 0
        
        for ticket in resolved:
            if ticket.created_at and ticket.updated_at:
                resolution_time = (ticket.updated_at - ticket.created_at).total_seconds() / 3600
                total_time += resolution_time
                count += 1
        
        return total_time / count if count > 0 else None
    
    def _get_sla_compliance_rate(self):
        """Get SLA compliance rate as percentage."""
        sla_tasks = OrderDisputeSLA.objects.filter(
            assigned_to=self.support_user,
            created_at__gte=self.start_date
        ).exclude(actual_resolution_time__isnull=True)
        
        if sla_tasks.count() == 0:
            return 0
        
        compliant = sla_tasks.filter(sla_breached=False).count()
        return (compliant / sla_tasks.count()) * 100
    
    def _get_customer_satisfaction(self):
        """Get customer satisfaction score (placeholder for future implementation)."""
        # TODO: Implement when customer satisfaction/rating system is available
        return None
    
    def _get_tickets_resolved_today(self):
        """Get count of tickets resolved today."""
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return Ticket.objects.filter(
            assigned_to=self.support_user,
            status='closed',
            updated_at__gte=today_start
        ).count()
    
    def _get_tickets_resolved_this_week(self):
        """Get count of tickets resolved this week."""
        week_start = timezone.now() - timedelta(days=7)
        return Ticket.objects.filter(
            assigned_to=self.support_user,
            status='closed',
            updated_at__gte=week_start
        ).count()

