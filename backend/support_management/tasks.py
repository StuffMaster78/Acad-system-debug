"""
Celery tasks for Support Management automation.
"""
from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from .models import (
    SupportDashboard, SupportWorkloadTracker, OrderDisputeSLA,
    SupportProfile
)
from .utils import check_sla_status, send_support_notification
from tickets.models import Ticket
from orders.models import Dispute, Order


@shared_task
def refresh_all_support_dashboards():
    """
    Automatically refresh all support dashboards.
    Runs every 15 minutes.
    """
    try:
        SupportDashboard.refresh_all_dashboards()
        return f"Refreshed {SupportDashboard.objects.count()} support dashboards"
    except Exception as e:
        return f"Error refreshing dashboards: {str(e)}"


@shared_task
def check_sla_breaches():
    """
    Check for SLA breaches and send alerts.
    Runs every 5 minutes.
    """
    try:
        from .services.sla_service import SLAService
        
        # Check and update all SLA statuses
        result = SLAService.check_and_update_all_slas()
        
        # Send warning alerts for approaching deadlines
        warning_count = SLAService.send_warning_alerts()
        
        # Send breach alerts
        breach_count = SLAService.send_breach_alerts()
        
        return f"SLA check completed: {result['checked']} checked, {result['new_breaches']} new breaches, {result['new_warnings']} new warnings, {breach_count} breach alerts sent, {warning_count} warning alerts sent"
    except Exception as e:
        return f"Error checking SLA breaches: {str(e)}"


@shared_task
def auto_reassign_unresolved_tasks():
    """
    Automatically reassign unresolved tasks from inactive agents.
    Runs every 30 minutes.
    """
    try:
        from .services.reassignment_service import SmartReassignmentService
        result = SmartReassignmentService.auto_reassign_inactive_agent_tasks()
        return f"Reassigned {result['reassigned_tickets']} tickets and {result['reassigned_disputes']} disputes"
    except Exception as e:
        return f"Error reassigning tasks: {str(e)}"


@shared_task
def update_support_workload_trackers():
    """
    Update workload statistics for all support agents.
    Runs every 10 minutes.
    """
    try:
        from .utils import update_support_workload
        
        support_profiles = SupportProfile.objects.filter(status='active')
        updated_count = 0
        
        for profile in support_profiles:
            try:
                update_support_workload(profile.user)
                updated_count += 1
            except Exception:
                continue
        
        return f"Updated workload for {updated_count} support agents"
    except Exception as e:
        return f"Error updating workload trackers: {str(e)}"


@shared_task
def send_sla_breach_alerts():
    """
    Send alerts for SLA breaches that haven't been resolved.
    Runs every 15 minutes.
    This task is now handled by check_sla_breaches, but kept for backward compatibility.
    """
    try:
        from .services.sla_service import SLAService
        breach_count = SLAService.send_breach_alerts()
        return f"Sent {breach_count} SLA breach alerts"
    except Exception as e:
        return f"Error sending SLA alerts: {str(e)}"


@shared_task
def calculate_support_performance_metrics():
    """
    Calculate and cache performance metrics for all support agents.
    Runs daily at 2 AM.
    """
    try:
        from .services.performance_service import SupportPerformanceService
        
        support_profiles = SupportProfile.objects.filter(status='active')
        calculated_count = 0
        
        for profile in support_profiles:
            try:
                service = SupportPerformanceService(profile.user)
                service.calculate_and_cache_metrics()
                calculated_count += 1
            except Exception:
                continue
        
        return f"Calculated performance metrics for {calculated_count} support agents"
    except Exception as e:
        return f"Error calculating performance metrics: {str(e)}"

