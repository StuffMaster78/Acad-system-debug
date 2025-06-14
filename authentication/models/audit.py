from django.db import models
from django.conf import settings
from django.utils import timezone
from authentication.utils.audit import get_client_ip

User = settings.AUTH_USER_MODEL

class AuditLog(models.Model):
    """
    Logs critical user actions including MFA changes, QR code scanning, etc.
    """
    ACTION_CHOICES = (
        ("MFA_ENABLED", "MFA Enabled"),
        ("MFA_DISABLED", "MFA Disabled"),
        ("MFA_RESET", "MFA Reset"),
        ("MFA_RECOVERY_REQUESTED", "MFA Recovery Requested"),
        ("MFA_CHALLENGE_REQUESTED", "MFA Challenge Requested"),
        ("MFA_CHALLANGE_VERIFIED", "MFA Challenge Verified"),
        ("MFA_RECOVERY_COMPLETED", "MFA Recovery Completed"),
        ("LOGIN_SUCCESS", "Login Successful"),
        ("LOGIN_FAILED", "Login Failed"),
        ("MFA_VERIFIED", "MFA Verified"),
        ("PASSWORD_RESET_REQUESTED", "Password Reset Requested"),
        ("PASSWORD_RESET_USED", "Password Reset Used"),
        ("MAGIC_LINK_REQUESTED", "Magic Link Requested"),
        ("MAGIC_LINK_USED", "Magic Link Used"),
        ("ACCOUNT_UPDATED", "Account Updated"),
        ("ACCOUNT_LOCKED", "Account Locked"),
        ("QR_CODE_GENERATED", "QR Code Generated"),
        ("QR_CODE_SCANNED", "QR Code Scanned"),
        ("DEVICE_DELETED", "Device Deleted"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs"
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="audit_logging_website"
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    device = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email}- {self.user} - {self.action} at {self.timestamp}"


    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    @staticmethod    
    def log_device_deletion(user, credential_id, request):
        """
        Logs the action of deleting a registered device (WebAuthn credential).
        """
        ip_address = get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown') if request else "Unknown"
        device = request.META.get('HTTP_X_DEVICE', 'Unknown Device')

        metadata = {
            "credential_id": credential_id,  # Store deleted credential ID for auditing
        }

        AuditLog.objects.create(
            user=user,
            action="DEVICE_DELETED",  # New action for device deletion
            ip_address=ip_address,
            user_agent=user_agent,
            device=device,
            metadata=metadata
        )
        
    @staticmethod    
    def log_mfa_action(user, action, request, metadata=None):
        """
        Logs an MFA-related action with metadata.
        """
        ip_address = get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown') if request else "Unknown"
        device = request.META.get('HTTP_X_DEVICE', 'Unknown Device')

        AuditLog.objects.create(
            user=user,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            device=device,
            metadata=metadata
        )

    @staticmethod
    def log_qr_code_action(user, action, qr_code_data=None, request=None):
        """
        Logs QR code related actions.
        """
        ip_address = get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown') if request else "Unknown"
        device = request.META.get('HTTP_X_DEVICE', 'Unknown Device')

        metadata = {
            "qr_code_data": qr_code_data,  
        }

        AuditLog.objects.create(
            user=user,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            device=device,
            metadata=metadata
        )