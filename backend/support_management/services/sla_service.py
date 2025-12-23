"""
Service for SLA monitoring and management.
"""
from django.utils import timezone
from django.db.models import Q, Count, Avg, F
from datetime import timedelta
from decimal import Decimal
from support_management.models import OrderDisputeSLA
from notifications_system.services.core import send_notification
import logging

logger = logging.getLogger(__name__)


class SLAService:
    """
    Service for managing SLA monitoring, alerts, and analytics.
    """
    
    @staticmethod
    def check_and_update_all_slas():
        """
        Check all active SLAs and update their status.
        Returns count of breaches and warnings.
        """
        active_slas = OrderDisputeSLA.objects.filter(
            actual_resolution_time__isnull=True
        ).select_related('assigned_to', 'order', 'dispute')
        
        breach_count = 0
        warning_count = 0
        
        for sla in active_slas:
            old_status = sla.status
            sla.check_sla_status()
            
            if sla.status == "breached" and old_status != "breached":
                breach_count += 1
            elif sla.status == "warning" and old_status not in ["warning", "breached"]:
                warning_count += 1
        
        return {
            "checked": active_slas.count(),
            "new_breaches": breach_count,
            "new_warnings": warning_count
        }
    
    @staticmethod
    def send_warning_alerts():
        """
        Send warning alerts for SLAs approaching deadline.
        """
        warning_slas = OrderDisputeSLA.objects.filter(
            status="warning",
            warning_sent_at__isnull=True,
            actual_resolution_time__isnull=True
        ).select_related('assigned_to')
        
        sent_count = 0
        for sla in warning_slas:
            if sla.assigned_to:
                try:
                    # Send in-app notification
                    send_notification(
                        user=sla.assigned_to,
                        notification_type='sla_warning',
                        title='SLA Warning: Approaching Deadline',
                        message=f"Your {sla.get_sla_type_display()} is approaching deadline. Time remaining: {sla.time_remaining_minutes} minutes.",
                        priority='medium',
                        metadata={
                            'sla_id': sla.id,
                            'sla_type': sla.sla_type,
                            'time_remaining_minutes': sla.time_remaining_minutes,
                            'order_id': sla.order.id if sla.order else None,
                            'dispute_id': sla.dispute.id if sla.dispute else None,
                        }
                    )
                    
                    # Send email warning
                    try:
                        from .email_service import EmailService
                        EmailService.send_sla_warning_email(
                            user=sla.assigned_to,
                            sla=sla
                        )
                    except Exception as e:
                        logger.warning(f"Could not send email warning for SLA {sla.id}: {e}")
                    
                    sla.warning_sent_at = timezone.now()
                    sla.save(update_fields=['warning_sent_at'])
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Error sending SLA warning for {sla.id}: {e}", exc_info=True)
        
        return sent_count
    
    @staticmethod
    def send_breach_alerts():
        """
        Send breach alerts for SLAs that have been breached.
        """
        breached_slas = OrderDisputeSLA.objects.filter(
            sla_breached=True,
            actual_resolution_time__isnull=True
        ).select_related('assigned_to', 'order', 'dispute')
        
        sent_count = 0
        for sla in breached_slas:
            if sla.assigned_to:
                try:
                    # Send in-app notification
                    send_notification(
                        user=sla.assigned_to,
                        notification_type='sla_breach',
                        title='🚨 SLA BREACH ALERT',
                        message=f"Your {sla.get_sla_type_display()} has been breached. Breach duration: {sla.breach_duration_minutes} minutes.",
                        priority='high',
                        metadata={
                            'sla_id': sla.id,
                            'sla_type': sla.sla_type,
                            'breach_duration_minutes': sla.breach_duration_minutes,
                            'order_id': sla.order.id if sla.order else None,
                            'dispute_id': sla.dispute.id if sla.dispute else None,
                        }
                    )
                    
                    # Send email alert if not already sent
                    if not sla.email_alert_sent:
                        try:
                            from .email_service import EmailService
                            EmailService.send_sla_breach_email(
                                user=sla.assigned_to,
                                sla=sla
                            )
                            sla.email_alert_sent = True
                        except Exception as e:
                            logger.warning(f"Could not send email alert for SLA {sla.id}: {e}")
                    
                    sla.breach_notified_at = timezone.now()
                    sla.save(update_fields=['breach_notified_at', 'email_alert_sent'])
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Error sending SLA breach alert for {sla.id}: {e}", exc_info=True)
        
        return sent_count
    
    @staticmethod
    def get_sla_metrics(assigned_to=None, sla_type=None, days=30):
        """
        Get SLA compliance metrics.
        
        Args:
            assigned_to: Filter by assigned support agent
            sla_type: Filter by SLA type
            days: Number of days to analyze
            
        Returns:
            dict with metrics
        """
        from_date = timezone.now() - timedelta(days=days)
        
        queryset = OrderDisputeSLA.objects.filter(created_at__gte=from_date)
        
        if assigned_to:
            queryset = queryset.filter(assigned_to=assigned_to)
        
        if sla_type:
            queryset = queryset.filter(sla_type=sla_type)
        
        total = queryset.count()
        resolved = queryset.filter(actual_resolution_time__isnull=False).count()
        breached = queryset.filter(sla_breached=True).count()
        active = queryset.filter(actual_resolution_time__isnull=True).count()
        active_breached = queryset.filter(
            actual_resolution_time__isnull=True,
            sla_breached=True
        ).count()
        active_warning = queryset.filter(
            actual_resolution_time__isnull=True,
            status="warning"
        ).count()
        
        # Calculate compliance rate (resolved on time / total resolved)
        resolved_on_time = queryset.filter(
            actual_resolution_time__isnull=False,
            sla_breached=False
        ).count()
        
        compliance_rate = (resolved_on_time / resolved * 100) if resolved > 0 else 0
        
        # Average resolution time
        resolved_slas = queryset.filter(actual_resolution_time__isnull=False)
        avg_resolution_time = None
        if resolved_slas.exists():
            resolution_times = []
            for sla in resolved_slas:
                if sla.actual_resolution_time and sla.created_at:
                    delta = sla.actual_resolution_time - sla.created_at
                    resolution_times.append(delta.total_seconds() / 3600)  # hours
            
            if resolution_times:
                avg_resolution_time = sum(resolution_times) / len(resolution_times)
        
        # Average breach duration
        breached_slas = queryset.filter(
            sla_breached=True,
            breach_duration_minutes__isnull=False
        )
        avg_breach_duration = None
        if breached_slas.exists():
            durations = [sla.breach_duration_minutes for sla in breached_slas if sla.breach_duration_minutes]
            if durations:
                avg_breach_duration = sum(durations) / len(durations)  # minutes
        
        return {
            "total_slas": total,
            "resolved": resolved,
            "breached": breached,
            "active": active,
            "active_breached": active_breached,
            "active_warning": active_warning,
            "compliance_rate": round(compliance_rate, 2),
            "resolved_on_time": resolved_on_time,
            "avg_resolution_time_hours": round(avg_resolution_time, 2) if avg_resolution_time else None,
            "avg_breach_duration_minutes": round(avg_breach_duration, 2) if avg_breach_duration else None,
            "period_days": days,
        }
    
    @staticmethod
    def get_agent_performance(assigned_to, days=30):
        """
        Get SLA performance metrics for a specific agent.
        """
        return SLAService.get_sla_metrics(assigned_to=assigned_to, days=days)
    
    @staticmethod
    def get_upcoming_deadlines(hours_ahead=24):
        """
        Get SLAs with deadlines in the next N hours.
        """
        from_date = timezone.now()
        to_date = timezone.now() + timedelta(hours=hours_ahead)
        
        return OrderDisputeSLA.objects.filter(
            expected_resolution_time__gte=from_date,
            expected_resolution_time__lte=to_date,
            actual_resolution_time__isnull=True
        ).select_related('assigned_to', 'order', 'dispute').order_by('expected_resolution_time')

