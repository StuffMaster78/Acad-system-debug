"""
Email service for SLA alerts.
"""
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending SLA-related emails.
    """
    
    @staticmethod
    def send_sla_breach_email(user, sla):
        """
        Send email alert for SLA breach.
        
        Args:
            user: User to send email to
            sla: OrderDisputeSLA instance
        """
        try:
            subject = f"🚨 SLA BREACH ALERT: {sla.get_sla_type_display()}"
            
            # Build context
            context = {
                'user': user,
                'sla': sla,
                'sla_type': sla.get_sla_type_display(),
                'breach_duration': f"{sla.breach_duration_minutes} minutes" if sla.breach_duration_minutes else "Unknown",
                'order_id': sla.order.id if sla.order else None,
                'dispute_id': sla.dispute.id if sla.dispute else None,
                'expected_time': sla.expected_resolution_time,
                'site_name': getattr(settings, 'SITE_NAME', 'Support System'),
            }
            
            # Try to render email template
            try:
                message = render_to_string('support_management/emails/sla_breach.html', context)
                message_plain = render_to_string('support_management/emails/sla_breach.txt', context)
            except Exception:
                # Fallback to plain text if template doesn't exist
                message_plain = f"""
SLA BREACH ALERT

Your {sla.get_sla_type_display()} has been breached.

Details:
- Type: {sla.get_sla_type_display()}
- Breach Duration: {context['breach_duration']}
- Expected Resolution: {sla.expected_resolution_time}
- {'Order ID' if sla.order else 'Dispute ID'}: {sla.order.id if sla.order else sla.dispute.id}

Please resolve this issue immediately.

Thank you,
Support Team
"""
                message = message_plain
            
            # Send email
            send_mail(
                subject=subject,
                message=message_plain,
                html_message=message if message != message_plain else None,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            logger.info(f"Sent SLA breach email to {user.email} for SLA {sla.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SLA breach email to {user.email}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def send_sla_warning_email(user, sla):
        """
        Send email warning for approaching SLA deadline.
        
        Args:
            user: User to send email to
            sla: OrderDisputeSLA instance
        """
        try:
            subject = f"⚠️ SLA WARNING: {sla.get_sla_type_display()} Approaching Deadline"
            
            # Build context
            context = {
                'user': user,
                'sla': sla,
                'sla_type': sla.get_sla_type_display(),
                'time_remaining': f"{sla.time_remaining_minutes} minutes" if sla.time_remaining_minutes else "Unknown",
                'order_id': sla.order.id if sla.order else None,
                'dispute_id': sla.dispute.id if sla.dispute else None,
                'expected_time': sla.expected_resolution_time,
                'site_name': getattr(settings, 'SITE_NAME', 'Support System'),
            }
            
            # Try to render email template
            try:
                message = render_to_string('support_management/emails/sla_warning.html', context)
                message_plain = render_to_string('support_management/emails/sla_warning.txt', context)
            except Exception:
                # Fallback to plain text if template doesn't exist
                message_plain = f"""
SLA WARNING

Your {sla.get_sla_type_display()} is approaching its deadline.

Details:
- Type: {sla.get_sla_type_display()}
- Time Remaining: {context['time_remaining']}
- Expected Resolution: {sla.expected_resolution_time}
- {'Order ID' if sla.order else 'Dispute ID'}: {sla.order.id if sla.order else sla.dispute.id}

Please take action to resolve this before the deadline.

Thank you,
Support Team
"""
                message = message_plain
            
            # Send email
            send_mail(
                subject=subject,
                message=message_plain,
                html_message=message if message != message_plain else None,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            logger.info(f"Sent SLA warning email to {user.email} for SLA {sla.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SLA warning email to {user.email}: {e}", exc_info=True)
            return False

