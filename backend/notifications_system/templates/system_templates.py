"""
System-related notification templates.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple
from notifications_system.templates.base import SystemNotificationTemplate
from notifications_system.registry.template_registry import register_template_class


@register_template_class("system.maintenance")
class SystemMaintenanceTemplate(SystemNotificationTemplate):
    """Template for system maintenance notifications."""
    
    event_name = "system.maintenance"
    priority = 8
    channels = ["email", "in_app"]
    
    def _render_template(
        self, 
        context: Dict[str, Any], 
        safe_context: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """Render system maintenance notification."""
        system_ctx = self._get_system_context(context)
        maintenance = context.get("maintenance", {})
        website = context.get("website", {})
        site_name = website.get("name", "Writing System")
        
        title = f"Scheduled Maintenance - {site_name}"
        
        start_time = maintenance.get("start_time", "TBD")
        end_time = maintenance.get("end_time", "TBD")
        duration = maintenance.get("duration", "Unknown")
        affected_services = maintenance.get("affected_services", ["All services"])
        
        text = f"""System Maintenance Notice

We will be performing scheduled maintenance on {site_name}.

Maintenance Details:
- Start Time: {start_time}
- End Time: {end_time}
- Duration: {duration}
- Affected Services: {', '.join(affected_services)}

During this time, some services may be temporarily unavailable. We apologize for any inconvenience.

We will notify you once maintenance is complete.

For updates, please check our status page or contact support.

Best regards,
The {site_name} Team"""
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #ffc107;">Scheduled Maintenance 🔧</h2>
            <p>We will be performing scheduled maintenance on {site_name}.</p>
            
            <div style="background: #fff3cd; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <h3 style="margin-top: 0; color: #856404;">Maintenance Details</h3>
                <ul style="list-style: none; padding: 0; color: #856404;">
                    <li><strong>Start Time:</strong> {start_time}</li>
                    <li><strong>End Time:</strong> {end_time}</li>
                    <li><strong>Duration:</strong> {duration}</li>
                    <li><strong>Affected Services:</strong> {', '.join(affected_services)}</li>
                </ul>
            </div>
            
            <div style="background: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #dc3545;">
                <p style="margin: 0; color: #721c24;">
                    <strong>Impact:</strong> During this time, some services may be temporarily unavailable. We apologize for any inconvenience.
                </p>
            </div>
            
            <div style="background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #007bff;">
                <p style="margin: 0; color: #004085;">
                    <strong>Updates:</strong> We will notify you once maintenance is complete. For updates, please check our status page or contact support.
                </p>
            </div>
            
            <p style="color: #6c757d; font-size: 14px;">
                Best regards,<br>
                The {site_name} Team
            </p>
        </div>
        """
        
        return title, text, html


@register_template_class("system.security_alert")
class SystemSecurityAlertTemplate(SystemNotificationTemplate):
    """Template for security alert notifications."""
    
    event_name = "system.security_alert"
    priority = 10
    channels = ["email", "in_app", "sms"]
    
    def _render_template(
        self, 
        context: Dict[str, Any], 
        safe_context: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """Render security alert notification."""
        system_ctx = self._get_system_context(context)
        security = context.get("security", {})
        website = context.get("website", {})
        site_name = website.get("name", "Writing System")
        
        title = f"SECURITY ALERT - {site_name}"
        
        alert_type = security.get("alert_type", "Security Incident")
        severity = security.get("severity", "High")
        description = security.get("description", "A security incident has been detected")
        action_required = security.get("action_required", "Please review your account security")
        
        text = f"""SECURITY ALERT

A security incident has been detected on your {site_name} account.

Alert Details:
- Type: {alert_type}
- Severity: {severity}
- Description: {description}
- Time: {system_ctx['timestamp']}

IMMEDIATE ACTION REQUIRED:
{action_required}

If you did not perform this action, please:
1. Change your password immediately
2. Review your account activity
3. Contact our security team

This is an automated security alert.

Best regards,
The {site_name} Security Team"""
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #dc3545;">SECURITY ALERT 🚨</h2>
            <p>A security incident has been detected on your {site_name} account.</p>
            
            <div style="background: #f8d7da; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #dc3545;">
                <h3 style="margin-top: 0; color: #721c24;">Alert Details</h3>
                <ul style="list-style: none; padding: 0; color: #721c24;">
                    <li><strong>Type:</strong> {alert_type}</li>
                    <li><strong>Severity:</strong> {severity}</li>
                    <li><strong>Description:</strong> {description}</li>
                    <li><strong>Time:</strong> {system_ctx['timestamp']}</li>
                </ul>
            </div>
            
            <div style="background: #dc3545; color: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: white;">IMMEDIATE ACTION REQUIRED:</h3>
                <p style="color: white; margin: 0;">{action_required}</p>
            </div>
            
            <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <p style="margin: 0; color: #856404;">
                    <strong>If you did not perform this action, please:</strong>
                </p>
                <ol style="color: #856404; margin: 10px 0;">
                    <li>Change your password immediately</li>
                    <li>Review your account activity</li>
                    <li>Contact our security team</li>
                </ol>
            </div>
            
            <p style="color: #6c757d; font-size: 14px; text-align: center;">
                This is an automated security alert.<br>
                Best regards,<br>
                The {site_name} Security Team
            </p>
        </div>
        """
        
        return title, text, html


@register_template_class("system.status_update")
class SystemStatusUpdateTemplate(SystemNotificationTemplate):
    """Template for system status update notifications."""
    
    event_name = "system.status_update"
    priority = 6
    channels = ["email", "in_app"]
    
    def _render_template(
        self, 
        context: Dict[str, Any], 
        safe_context: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """Render system status update notification."""
        system_ctx = self._get_system_context(context)
        status = context.get("status", {})
        website = context.get("website", {})
        site_name = website.get("name", "Writing System")
        
        status_type = status.get("type", "Update")
        status_message = status.get("message", "System status has been updated")
        affected_services = status.get("affected_services", ["All services"])
        resolution_time = status.get("resolution_time", "Unknown")
        
        title = f"System Status Update - {status_type}"
        
        text = f"""System Status Update

{status_message}

Status Details:
- Type: {status_type}
- Affected Services: {', '.join(affected_services)}
- Resolution Time: {resolution_time}
- Update Time: {system_ctx['timestamp']}

We are working to resolve any issues as quickly as possible.

For real-time updates, please check our status page.

Best regards,
The {site_name} Team"""
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #007bff;">System Status Update 📊</h2>
            <p>{status_message}</p>
            
            <div style="background: #e7f3ff; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #007bff;">
                <h3 style="margin-top: 0; color: #004085;">Status Details</h3>
                <ul style="list-style: none; padding: 0; color: #004085;">
                    <li><strong>Type:</strong> {status_type}</li>
                    <li><strong>Affected Services:</strong> {', '.join(affected_services)}</li>
                    <li><strong>Resolution Time:</strong> {resolution_time}</li>
                    <li><strong>Update Time:</strong> {system_ctx['timestamp']}</li>
                </ul>
            </div>
            
            <div style="background: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #17a2b8;">
                <p style="margin: 0; color: #0c5460;">
                    <strong>Status:</strong> We are working to resolve any issues as quickly as possible.
                </p>
            </div>
            
            <p style="color: #6c757d; font-size: 14px;">
                For real-time updates, please check our status page.<br>
                Best regards,<br>
                The {site_name} Team
            </p>
        </div>
        """
        
        return title, text, html
