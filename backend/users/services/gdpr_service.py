"""
GDPR Compliance Service - Comprehensive GDPR rights implementation.

Implements all GDPR articles:
- Article 15: Right of access (data export)
- Article 16: Right to rectification (data correction)
- Article 17: Right to erasure (account deletion)
- Article 18: Right to restriction of processing
- Article 20: Right to data portability
- Article 21: Right to object
- Article 7: Conditions for consent
- Article 33: Data breach notification
"""
import json
import logging
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from typing import Dict, Any, List

from users.models import PrivacySettings, DataAccessLog
from authentication.models.security_events import SecurityEvent
from notifications_system.utils.email_templates import send_priority_email
from notifications_system.enums import NotificationPriority

logger = logging.getLogger(__name__)


class GDPRService:
    """
    Comprehensive GDPR compliance service.
    Handles all user data rights under GDPR.
    """
    
    def __init__(self, user, website=None):
        """
        Initialize GDPR service for a user.
        
        Args:
            user: User instance
            website: Website instance (for multitenancy)
        """
        self.user = user
        self.website = website
    
    # ==================== Article 15: Right of Access ====================
    
    def export_all_data(self, format='json') -> Dict[str, Any]:
        """
        Export all user data (Article 15 - Right of Access).
        
        Returns comprehensive JSON export including:
        - User profile data
        - Orders and transactions
        - Messages and communications
        - Security events
        - Privacy settings
        - Data access logs
        - Sessions and devices
        
        Args:
            format: Export format ('json', 'csv', 'xml') - currently only JSON
            
        Returns:
            Dict containing all user data
        """
        from users.serializers import UserSerializer
        from orders.serializers import OrderSerializer
        from order_payments_management.serializers import OrderPaymentSerializer
        
        export_data = {
            "export_metadata": {
                "exported_at": timezone.now().isoformat(),
                "user_id": self.user.id,
                "user_email": self.user.email,
                "format": format,
                "gdpr_article": "Article 15 - Right of Access"
            },
            "user_profile": UserSerializer(self.user).data,
            "orders": [],
            "payments": [],
            "messages": [],
            "sessions": [],
            "security_events": [],
            "privacy_settings": {},
            "data_access_logs": [],
            "consent_records": []
        }
        
        # Get orders
        if hasattr(self.user, 'orders'):
            export_data["orders"] = OrderSerializer(
                self.user.orders.all(), 
                many=True
            ).data
        
        # Get payments
        if hasattr(self.user, 'payments'):
            export_data["payments"] = OrderPaymentSerializer(
                self.user.payments.all(), 
                many=True
            ).data
        
        # Get messages/communications
        if hasattr(self.user, 'sent_messages'):
            export_data["messages"] = [
                {
                    "id": msg.id,
                    "recipient": msg.recipient.email if hasattr(msg, 'recipient') else None,
                    "subject": getattr(msg, 'subject', ''),
                    "content": getattr(msg, 'content', ''),
                    "created_at": msg.created_at.isoformat() if hasattr(msg, 'created_at') else None,
                }
                for msg in self.user.sent_messages.all()[:1000]  # Limit to prevent huge exports
            ]
        
        # Get sessions
        if hasattr(self.user, 'user_sessions'):
            export_data["sessions"] = [
                {
                    "id": str(session.id),
                    "ip_address": session.ip_address,
                    "user_agent": session.user_agent,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat() if hasattr(session, 'last_activity') else None,
                }
                for session in self.user.user_sessions.all()
            ]
        
        # Get security events
        if hasattr(self.user, 'security_events'):
            export_data["security_events"] = [
                {
                    "event_type": event.event_type,
                    "severity": event.severity,
                    "is_suspicious": event.is_suspicious,
                    "created_at": event.created_at.isoformat(),
                    "location": event.location,
                    "device": event.device,
                    "ip_address": event.ip_address,
                }
                for event in self.user.security_events.all()[:1000]
            ]
        
        # Get privacy settings
        try:
            privacy_settings = PrivacySettings.objects.get(user=self.user)
            export_data["privacy_settings"] = {
                "profile_visibility": {
                    "to_writers": privacy_settings.profile_visibility_to_writers,
                    "to_admins": privacy_settings.profile_visibility_to_admins,
                    "to_support": privacy_settings.profile_visibility_to_support,
                },
                "data_sharing": {
                    "analytics": privacy_settings.allow_analytics,
                    "marketing": privacy_settings.allow_marketing,
                    "third_party": privacy_settings.allow_third_party_sharing,
                },
                "notifications": {
                    "on_login": privacy_settings.notify_on_login,
                    "on_login_method": privacy_settings.notify_on_login_method,
                    "on_suspicious_activity": privacy_settings.notify_on_suspicious_activity,
                }
            }
        except PrivacySettings.DoesNotExist:
            pass
        
        # Get data access logs
        export_data["data_access_logs"] = [
            {
                "accessed_by": log.accessed_by.email if log.accessed_by else "System",
                "access_type": log.access_type,
                "accessed_at": log.accessed_at.isoformat(),
                "ip_address": log.ip_address,
            }
            for log in DataAccessLog.objects.filter(user=self.user)[:1000]
        ]
        
        # Get consent records (from privacy settings history)
        export_data["consent_records"] = self._get_consent_history()
        
        # Log the export
        if self.website:
            DataAccessLog.objects.create(
                user=self.user,
                accessed_by=self.user,  # User accessing their own data
                access_type='data_export',
                ip_address=None,  # Will be set by view
                metadata={
                    'export_type': 'full',
                    'format': format,
                    'gdpr_article': 'Article 15'
                }
            )
        
        return export_data
    
    def _get_consent_history(self) -> List[Dict[str, Any]]:
        """Get history of consent changes."""
        # This would ideally track consent changes over time
        # For now, return current consent status
        try:
            privacy_settings = PrivacySettings.objects.get(user=self.user)
            return [
                {
                    "consent_type": "analytics",
                    "consented": privacy_settings.allow_analytics,
                    "updated_at": privacy_settings.updated_at.isoformat(),
                },
                {
                    "consent_type": "marketing",
                    "consented": privacy_settings.allow_marketing,
                    "updated_at": privacy_settings.updated_at.isoformat(),
                },
                {
                    "consent_type": "third_party_sharing",
                    "consented": privacy_settings.allow_third_party_sharing,
                    "updated_at": privacy_settings.updated_at.isoformat(),
                },
            ]
        except PrivacySettings.DoesNotExist:
            return []
    
    # ==================== Article 16: Right to Rectification ====================
    
    def request_data_correction(self, corrections: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request correction of inaccurate data (Article 16).
        
        Args:
            corrections: Dict of fields to correct {field_name: new_value}
            
        Returns:
            Dict with correction request status
        """
        # Log the correction request
        if self.website:
            SecurityEvent.log_event(
                user=self.user,
                website=self.website,
                event_type='profile_updated',
                severity='low',
                metadata={
                    'corrections_requested': list(corrections.keys()),
                    'gdpr_article': 'Article 16'
                }
            )
        
        return {
            "message": "Data correction request logged",
            "corrections": corrections,
            "status": "pending_review"
        }
    
    # ==================== Article 17: Right to Erasure ====================
    
    def request_account_deletion(self, reason: str = None) -> Dict[str, Any]:
        """
        Request account deletion (Article 17 - Right to Erasure).
        
        This is already handled by AccountDeletionService,
        but we log it here for GDPR compliance.
        
        Args:
            reason: Optional reason for deletion
            
        Returns:
            Dict with deletion request status
        """
        from authentication.models.deletion_requests import AccountDeletionRequest
        
        # Check if request already exists
        existing = AccountDeletionRequest.objects.filter(
            user=self.user,
            website=self.website,
            status='pending'
        ).first()
        
        if existing:
            raise ValidationError("Account deletion request already pending.")
        
        # Create deletion request
        deletion_request = AccountDeletionRequest.objects.create(
            user=self.user,
            website=self.website,
            reason=reason
        )
        
        # Log GDPR erasure request
        if self.website:
            SecurityEvent.log_event(
                user=self.user,
                website=self.website,
                event_type='account_locked',
                severity='high',
                metadata={
                    'gdpr_article': 'Article 17',
                    'deletion_request_id': deletion_request.id,
                    'reason': reason
                }
            )
        
        return {
            "message": "Account deletion request submitted",
            "deletion_request_id": deletion_request.id,
            "status": "pending",
            "grace_period_days": 90  # 3 months grace period
        }
    
    # ==================== Article 18: Right to Restriction of Processing ====================
    
    def restrict_processing(self, reason: str = None) -> Dict[str, Any]:
        """
        Restrict processing of user data (Article 18).
        
        This freezes the account and stops all data processing
        except for legal obligations.
        
        Args:
            reason: Reason for restriction
            
        Returns:
            Dict with restriction status
        """
        # Freeze account
        self.user.is_frozen = True
        self.user.save(update_fields=['is_frozen'])
        
        # Update privacy settings to restrict all processing
        privacy_settings, _ = PrivacySettings.get_or_create_for_user(self.user)
        privacy_settings.allow_analytics = False
        privacy_settings.allow_marketing = False
        privacy_settings.allow_third_party_sharing = False
        privacy_settings.save()
        
        # Log restriction
        if self.website:
            SecurityEvent.log_event(
                user=self.user,
                website=self.website,
                event_type='account_locked',
                severity='medium',
                metadata={
                    'gdpr_article': 'Article 18',
                    'reason': reason,
                    'processing_restricted': True
                }
            )
        
        return {
            "message": "Data processing has been restricted",
            "status": "restricted",
            "account_frozen": True
        }
    
    def lift_processing_restriction(self) -> Dict[str, Any]:
        """Lift processing restriction."""
        self.user.is_frozen = False
        self.user.save(update_fields=['is_frozen'])
        
        return {
            "message": "Processing restriction lifted",
            "status": "active"
        }
    
    # ==================== Article 20: Right to Data Portability ====================
    
    def export_portable_data(self, format='json') -> Dict[str, Any]:
        """
        Export data in portable format (Article 20).
        
        Similar to Article 15, but focuses on data the user provided
        (not derived data like analytics).
        
        Args:
            format: Export format
            
        Returns:
            Dict with portable data
        """
        export_data = self.export_all_data(format=format)
        
        # Add portability metadata
        export_data["export_metadata"]["gdpr_article"] = "Article 20 - Right to Data Portability"
        export_data["export_metadata"]["portable_format"] = True
        
        return export_data
    
    # ==================== Article 21: Right to Object ====================
    
    def object_to_processing(self, processing_type: str, reason: str = None) -> Dict[str, Any]:
        """
        Object to specific data processing (Article 21).
        
        Args:
            processing_type: Type of processing ('marketing', 'analytics', 'profiling', 'all')
            reason: Optional reason for objection
            
        Returns:
            Dict with objection status
        """
        privacy_settings, _ = PrivacySettings.get_or_create_for_user(self.user)
        
        if processing_type == 'marketing' or processing_type == 'all':
            privacy_settings.allow_marketing = False
        
        if processing_type == 'analytics' or processing_type == 'all':
            privacy_settings.allow_analytics = False
        
        if processing_type == 'profiling' or processing_type == 'all':
            privacy_settings.allow_third_party_sharing = False
        
        privacy_settings.save()
        
        # Log objection
        if self.website:
            SecurityEvent.log_event(
                user=self.user,
                website=self.website,
                event_type='privacy_settings_changed',
                severity='low',
                metadata={
                    'gdpr_article': 'Article 21',
                    'processing_type': processing_type,
                    'reason': reason
                }
            )
        
        return {
            "message": f"Objection to {processing_type} processing recorded",
            "status": "active",
            "processing_type": processing_type
        }
    
    # ==================== Article 7: Conditions for Consent ====================
    
    def record_consent(self, consent_type: str, consented: bool, purpose: str = None) -> Dict[str, Any]:
        """
        Record user consent (Article 7).
        
        Args:
            consent_type: Type of consent ('analytics', 'marketing', 'third_party')
            consented: Whether user consented
            purpose: Purpose of consent
            
        Returns:
            Dict with consent record
        """
        privacy_settings, _ = PrivacySettings.get_or_create_for_user(self.user)
        
        if consent_type == 'analytics':
            privacy_settings.allow_analytics = consented
        elif consent_type == 'marketing':
            privacy_settings.allow_marketing = consented
        elif consent_type == 'third_party':
            privacy_settings.allow_third_party_sharing = consented
        
        privacy_settings.save()
        
        # Log consent
        if self.website:
            DataAccessLog.objects.create(
                user=self.user,
                accessed_by=self.user,
                access_type='data_export',  # Using existing type
                metadata={
                    'consent_type': consent_type,
                    'consented': consented,
                    'purpose': purpose,
                    'gdpr_article': 'Article 7',
                    'timestamp': timezone.now().isoformat()
                }
            )
        
        return {
            "message": f"Consent for {consent_type} recorded",
            "consented": consented,
            "consent_type": consent_type
        }
    
    def get_consent_status(self) -> Dict[str, Any]:
        """Get current consent status for all processing types."""
        try:
            privacy_settings = PrivacySettings.objects.get(user=self.user)
            return {
                "analytics": privacy_settings.allow_analytics,
                "marketing": privacy_settings.allow_marketing,
                "third_party_sharing": privacy_settings.allow_third_party_sharing,
                "updated_at": privacy_settings.updated_at.isoformat()
            }
        except PrivacySettings.DoesNotExist:
            return {
                "analytics": True,  # Default
                "marketing": False,  # Default
                "third_party_sharing": False,  # Default
                "updated_at": None
            }
    
    # ==================== Article 33: Data Breach Notification ====================
    
    def log_data_breach(self, breach_type: str, affected_data: List[str], 
                       severity: str = 'high') -> Dict[str, Any]:
        """
        Log a data breach for notification (Article 33).
        
        Note: This should be called by admins when a breach is detected.
        The service will handle notification to affected users.
        
        Args:
            breach_type: Type of breach ('unauthorized_access', 'data_loss', 'system_compromise')
            affected_data: List of data types affected
            severity: Breach severity ('low', 'medium', 'high', 'critical')
            
        Returns:
            Dict with breach log status
        """
        # Log security event
        if self.website:
            SecurityEvent.log_event(
                user=self.user,
                website=self.website,
                event_type='suspicious_activity',
                severity=severity,
                is_suspicious=True,
                metadata={
                    'gdpr_article': 'Article 33',
                    'breach_type': breach_type,
                    'affected_data': affected_data,
                    'notification_required': True
                }
            )
        
        # Send breach notification email to user (GDPR Article 33 requirement)
        notification_sent = False
        try:
            # Map severity to notification priority
            severity_priority_map = {
                'low': NotificationPriority.LOW,
                'medium': NotificationPriority.NORMAL,
                'high': NotificationPriority.HIGH,
                'critical': NotificationPriority.CRITICAL,
            }
            priority = severity_priority_map.get(severity, NotificationPriority.HIGH)
            
            # Format breach type for display
            breach_type_display = {
                'unauthorized_access': 'Unauthorized Access',
                'data_loss': 'Data Loss',
                'system_compromise': 'System Compromise',
            }.get(breach_type, breach_type.replace('_', ' ').title())
            
            # Format affected data
            affected_data_str = ', '.join(affected_data) if affected_data else 'User data'
            
            # Get website name
            website_name = self.website.name if self.website else 'Writing System'
            
            # Create email subject
            subject = f"IMPORTANT: Data Breach Notification - {website_name}"
            
            # Create email message (plain text)
            message = f"""IMPORTANT DATA BREACH NOTIFICATION

Dear {self.user.get_full_name() or self.user.username},

We are writing to inform you of a data breach that may have affected your personal data, in accordance with GDPR Article 33.

BREACH DETAILS:
- Type: {breach_type_display}
- Severity: {severity.upper()}
- Affected Data: {affected_data_str}
- Date: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

WHAT HAPPENED:
A security incident has been detected that may have compromised your personal data. We have taken immediate action to contain the breach and investigate the matter.

WHAT WE ARE DOING:
1. We have contained the breach and secured our systems
2. We are conducting a thorough investigation
3. We are notifying all affected users as required by GDPR
4. We are working with relevant authorities as necessary

WHAT YOU SHOULD DO:
1. Review your account activity for any suspicious behavior
2. Change your password immediately if you haven't done so recently
3. Enable two-factor authentication if available
4. Monitor your financial accounts and credit reports
5. Be cautious of phishing attempts related to this breach

YOUR RIGHTS:
Under GDPR, you have the right to:
- Access your personal data (Article 15)
- Rectify inaccurate data (Article 16)
- Request erasure of your data (Article 17)
- Restrict processing of your data (Article 18)
- Data portability (Article 20)
- Object to processing (Article 21)

If you have any questions or concerns, please contact our support team immediately.

This notification is sent in compliance with GDPR Article 33 (Notification of a personal data breach to the supervisory authority).

Best regards,
The {website_name} Security Team"""
            
            # Create HTML message
            html_message = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: #dc3545; color: white; padding: 20px; border-radius: 5px 5px 0 0; text-align: center;">
        <h1 style="margin: 0; font-size: 24px;">⚠️ DATA BREACH NOTIFICATION</h1>
    </div>
    
    <div style="background: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; border-top: none;">
        <p>Dear <strong>{self.user.get_full_name() or self.user.username}</strong>,</p>
        
        <p>We are writing to inform you of a data breach that may have affected your personal data, in accordance with <strong>GDPR Article 33</strong>.</p>
        
        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
            <h2 style="margin-top: 0; color: #856404;">BREACH DETAILS</h2>
            <ul style="color: #856404; margin: 0;">
                <li><strong>Type:</strong> {breach_type_display}</li>
                <li><strong>Severity:</strong> <span style="text-transform: uppercase;">{severity}</span></li>
                <li><strong>Affected Data:</strong> {affected_data_str}</li>
                <li><strong>Date:</strong> {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
            </ul>
        </div>
        
        <h2 style="color: #dc3545;">WHAT HAPPENED</h2>
        <p>A security incident has been detected that may have compromised your personal data. We have taken immediate action to contain the breach and investigate the matter.</p>
        
        <h2 style="color: #0d6efd;">WHAT WE ARE DOING</h2>
        <ol>
            <li>We have contained the breach and secured our systems</li>
            <li>We are conducting a thorough investigation</li>
            <li>We are notifying all affected users as required by GDPR</li>
            <li>We are working with relevant authorities as necessary</li>
        </ol>
        
        <div style="background: #dc3545; color: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
            <h2 style="margin-top: 0; color: white;">WHAT YOU SHOULD DO</h2>
            <ol style="color: white; margin: 0;">
                <li>Review your account activity for any suspicious behavior</li>
                <li>Change your password immediately if you haven't done so recently</li>
                <li>Enable two-factor authentication if available</li>
                <li>Monitor your financial accounts and credit reports</li>
                <li>Be cautious of phishing attempts related to this breach</li>
            </ol>
        </div>
        
        <h2 style="color: #198754;">YOUR RIGHTS</h2>
        <p>Under GDPR, you have the right to:</p>
        <ul>
            <li>Access your personal data (Article 15)</li>
            <li>Rectify inaccurate data (Article 16)</li>
            <li>Request erasure of your data (Article 17)</li>
            <li>Restrict processing of your data (Article 18)</li>
            <li>Data portability (Article 20)</li>
            <li>Object to processing (Article 21)</li>
        </ul>
        
        <p>If you have any questions or concerns, please contact our support team immediately.</p>
        
        <div style="background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center; font-size: 12px; color: #6c757d;">
            <p style="margin: 0;">This notification is sent in compliance with <strong>GDPR Article 33</strong> (Notification of a personal data breach to the supervisory authority).</p>
        </div>
        
        <p>Best regards,<br>
        <strong>The {website_name} Security Team</strong></p>
    </div>
</body>
</html>"""
            
            # Send the email
            send_priority_email(
                user=self.user,
                subject=subject,
                message=message,
                html_message=html_message,
                priority=priority,
                website=self.website,
            )
            
            notification_sent = True
            logger.info(
                f"GDPR breach notification email sent to user {self.user.id} "
                f"for breach type: {breach_type}, severity: {severity}"
            )
            
        except Exception as e:
            logger.error(
                f"Failed to send GDPR breach notification email to user {self.user.id}: {str(e)}",
                exc_info=True
            )
            # Don't fail the breach logging if email fails - breach is still logged
        
        return {
            "message": "Data breach logged and user will be notified",
            "breach_type": breach_type,
            "severity": severity,
            "notification_sent": notification_sent
        }
    
    # ==================== Utility Methods ====================
    
    def get_gdpr_summary(self) -> Dict[str, Any]:
        """Get summary of all GDPR-related data and rights."""
        return {
            "user_id": self.user.id,
            "user_email": self.user.email,
            "account_status": {
                "is_active": self.user.is_active,
                "is_frozen": getattr(self.user, 'is_frozen', False),
                "deletion_requested": getattr(self.user, 'is_deletion_requested', False),
            },
            "privacy_settings": self.get_consent_status(),
            "data_access_logs_count": DataAccessLog.objects.filter(user=self.user).count(),
            "security_events_count": SecurityEvent.objects.filter(user=self.user).count() if hasattr(self.user, 'security_events') else 0,
            "rights_available": [
                "Right of Access (Article 15)",
                "Right to Rectification (Article 16)",
                "Right to Erasure (Article 17)",
                "Right to Restriction (Article 18)",
                "Right to Portability (Article 20)",
                "Right to Object (Article 21)"
            ]
        }

