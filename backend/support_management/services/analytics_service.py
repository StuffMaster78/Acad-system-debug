"""
Analytics Service for Support Management
"""
from django.db.models import Avg, Count, Q, F, Sum
from django.utils import timezone
from datetime import timedelta
from tickets.models import Ticket, TicketMessage
from orders.models import Dispute, Order
from support_management.models import SupportProfile, SupportWorkloadTracker, OrderDisputeSLA


class SupportAnalyticsService:
    """
    Service for calculating support analytics and metrics.
    """
    
    def __init__(self, support_user=None, days=30):
        """
        Initialize analytics service.
        
        Args:
            support_user: Specific support user to analyze (None for all)
            days: Number of days to analyze (default: 30)
        """
        self.support_user = support_user
        self.days = days
        self.start_date = timezone.now() - timedelta(days=days)
    
    def get_performance_analytics(self):
        """
        Get performance analytics for support team or individual agent.
        
        Returns:
            dict: Performance metrics including response times, resolution rates, etc.
        """
        if self.support_user:
            tickets = Ticket.objects.filter(
                assigned_to=self.support_user,
                created_at__gte=self.start_date
            )
        else:
            tickets = Ticket.objects.filter(created_at__gte=self.start_date)
        
        resolved = tickets.filter(status='closed')
        
        # Calculate average resolution time
        avg_resolution_time = self._calculate_avg_resolution_time(resolved)
        
        # Calculate average first response time
        avg_response_time = self._calculate_avg_response_time(tickets)
        
        # Resolution rate
        resolution_rate = (resolved.count() / tickets.count() * 100) if tickets.count() > 0 else 0
        
        # SLA compliance
        sla_compliance = self._calculate_sla_compliance()
        
        return {
            'tickets_handled': tickets.count(),
            'tickets_resolved': resolved.count(),
            'resolution_rate_percent': round(resolution_rate, 2),
            'avg_resolution_time_hours': round(avg_resolution_time, 2) if avg_resolution_time else None,
            'avg_response_time_hours': round(avg_response_time, 2) if avg_response_time else None,
            'sla_compliance_rate_percent': round(sla_compliance, 2),
        }
    
    def get_trend_analytics(self):
        """
        Get trend analytics (weekly breakdown).
        
        Returns:
            list: Weekly trend data
        """
        trends = []
        weeks = self.days // 7
        
        for week in range(weeks):
            week_start = self.start_date + timedelta(weeks=week)
            week_end = week_start + timedelta(days=7)
            
            if self.support_user:
                week_tickets = Ticket.objects.filter(
                    assigned_to=self.support_user,
                    created_at__gte=week_start,
                    created_at__lt=week_end
                )
                week_resolved = week_tickets.filter(status='closed')
            else:
                week_tickets = Ticket.objects.filter(
                    created_at__gte=week_start,
                    created_at__lt=week_end
                )
                week_resolved = week_tickets.filter(status='closed')
            
            trends.append({
                'week': week + 1,
                'week_start': week_start.date().isoformat(),
                'week_end': week_end.date().isoformat(),
                'tickets_created': week_tickets.count(),
                'tickets_resolved': week_resolved.count(),
                'resolution_rate': (week_resolved.count() / week_tickets.count() * 100) if week_tickets.count() > 0 else 0,
            })
        
        return trends
    
    def get_agent_comparison(self):
        """
        Compare performance across all support agents.
        
        Returns:
            list: Performance metrics for each agent
        """
        agents = SupportProfile.objects.filter(status='active')
        comparison = []
        
        for agent in agents:
            service = SupportAnalyticsService(support_user=agent.user, days=self.days)
            performance = service.get_performance_analytics()
            
            comparison.append({
                'agent_id': agent.id,
                'agent_name': agent.name,
                'registration_id': agent.registration_id,
                **performance
            })
        
        return comparison
    
    def get_sla_analytics(self):
        """
        Get SLA compliance analytics.
        
        Returns:
            dict: SLA metrics
        """
        if self.support_user:
            sla_tasks = OrderDisputeSLA.objects.filter(
                assigned_to=self.support_user,
                created_at__gte=self.start_date
            )
        else:
            sla_tasks = OrderDisputeSLA.objects.filter(created_at__gte=self.start_date)
        
        total = sla_tasks.count()
        breached = sla_tasks.filter(sla_breached=True).count()
        resolved_on_time = sla_tasks.filter(
            sla_breached=False,
            actual_resolution_time__isnull=False
        ).count()
        
        compliance_rate = (resolved_on_time / total * 100) if total > 0 else 0
        
        return {
            'total_sla_tasks': total,
            'breached_count': breached,
            'resolved_on_time': resolved_on_time,
            'compliance_rate_percent': round(compliance_rate, 2),
            'breach_rate_percent': round((breached / total * 100) if total > 0 else 0, 2),
        }
    
    def get_workload_distribution(self):
        """
        Get workload distribution across support team.
        
        Returns:
            list: Workload data for each agent
        """
        agents = SupportProfile.objects.filter(status='active')
        distribution = []
        
        for agent in agents:
            try:
                workload = SupportWorkloadTracker.objects.get(support_staff=agent.user)
                current_tickets = Ticket.objects.filter(
                    assigned_to=agent.user,
                    status__in=['open', 'in_progress']
                ).count()
                
                distribution.append({
                    'agent_id': agent.id,
                    'agent_name': agent.name,
                    'current_ticket_load': current_tickets,
                    'tickets_handled': workload.tickets_handled,
                    'disputes_handled': workload.disputes_handled,
                    'orders_managed': workload.orders_managed,
                    'total_workload': workload.tickets_handled + workload.disputes_handled + workload.orders_managed,
                })
            except SupportWorkloadTracker.DoesNotExist:
                continue
        
        return distribution
    
    def _calculate_avg_resolution_time(self, tickets):
        """Calculate average resolution time in hours."""
        if not tickets.exists():
            return None
        
        total_time = 0
        count = 0
        
        for ticket in tickets:
            if ticket.created_at and ticket.updated_at and ticket.status == 'closed':
                resolution_time = (ticket.updated_at - ticket.created_at).total_seconds() / 3600
                total_time += resolution_time
                count += 1
        
        return total_time / count if count > 0 else None
    
    def _calculate_avg_response_time(self, tickets):
        """Calculate average first response time in hours."""
        if not tickets.exists():
            return None
        
        response_times = []
        
        for ticket in tickets:
            first_message = TicketMessage.objects.filter(
                ticket=ticket,
                sender=ticket.assigned_to
            ).order_by('created_at').first()
            
            if first_message and ticket.created_at:
                response_time = (first_message.created_at - ticket.created_at).total_seconds() / 3600
                response_times.append(response_time)
        
        return sum(response_times) / len(response_times) if response_times else None
    
    def _calculate_sla_compliance(self):
        """Calculate SLA compliance rate."""
        if self.support_user:
            sla_tasks = OrderDisputeSLA.objects.filter(
                assigned_to=self.support_user,
                created_at__gte=self.start_date
            )
        else:
            sla_tasks = OrderDisputeSLA.objects.filter(created_at__gte=self.start_date)
        
        total = sla_tasks.exclude(actual_resolution_time__isnull=True).count()
        compliant = sla_tasks.filter(
            sla_breached=False,
            actual_resolution_time__isnull=False
        ).count()
        
        return (compliant / total * 100) if total > 0 else 0

