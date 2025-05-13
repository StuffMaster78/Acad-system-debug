from django.conf import settings
from django.utils.timezone import now
import pyotp
import random
import string
from django.core.mail import send_mail
from twilio.rest import Client
import redis
from datetime import timedelta
#  Fancy 
import qrcode
import requests
from io import BytesIO
from django.conf import settings
from rest_framework.exceptions import PermissionDenied
from user_agents import parse
from django.contrib.sessions.models import Session





def logout_all_sessions(user):
    """
    Logs out the user from all active sessions.
    """
     # Get all sessions where the user is authenticated
    sessions = Session.objects.filter(
        session_data__contains=f"user_id:{user.id}"
    )
    # Delete all sessions for this user
    sessions.delete()
    # Invalidate the user's current session (this happens automatically after logout)
    if hasattr(user, "auth_token"):
        user.auth_token.delete()
# If you want to clear cookies or token for the client-side, you might want to set the session cookie to expire
    # within the response in your views
    return True


def get_client_ip(requests):
    """
    Extracts the real client IP address from request headers.
    Supports proxies by checking `HTTP_X_FORWARDED_FOR`.
    """
    x_forwarded_for = requests.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # Get the first IP (real IP)
    else:
        ip = requests.META.get('REMOTE_ADDR')  # Fallback to remote address
    return ip



def send_deletion_confirmation_email(user):
    """
    Sends a confirmation email to the user requesting account deletion.
    """
    from users.models import AccountDeletionRequest, AuditLog

    subject = "Confirm Your Account Deletion Request"
    confirmation_link = f"https://{user.website.domain}/confirm-deletion/{user.id}"
    
    message = f"""
    Hello {user.username},

    We received your request to delete your account. To proceed with the deletion, please confirm by clicking the link below:

    {confirmation_link}

    If you did not request this, please ignore this email, and your account will remain active.

    Regards,
    {user.website.name} Support Team
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

    # Log request timestamp
    AccountDeletionRequest.objects.create(
        user=user,
        reason="Pending Confirmation",
        requested_at=now()
    )




def generate_otp():
    """Generates a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(user, otp):
    """Sends OTP to user's email."""
    subject = "Your Login OTP"
    message = f"Your OTP for login is: {otp}. It will expire in 10 minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

def send_otp_sms(user, otp):
    """Sends OTP via SMS using Twilio."""
    if not user.phone_number:
        return False
    
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = f"Your OTP for login is: {otp}. It will expire in 10 minutes."
    
    client.messages.create(
        body=message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=user.phone_number
    )
    return True

def verify_totp(user, otp):
    """Verifies TOTP (Google Authenticator) code."""
    if not user.mfa_secret:
        return False
    totp = pyotp.TOTP(user.mfa_secret)
    return totp.verify(otp)

def generate_totp_qr_code(user):
    """
    Generate a QR Code for TOTP-based authentication.
    """
    if not user.mfa_secret:
        user.generate_mfa_secret()

    otp_uri = pyotp.totp.TOTP(user.mfa_secret).provisioning_uri(
        name=user.email,
        issuer_name="YourApp"
    )

    qr = qrcode.make(otp_uri)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    return buffer.getvalue()

def send_unlock_email(user):
    """Send unlock instructions to the user's email."""
    unlock_link = f"https://{user.website.domain}/unlock/{user.id}"
    
    send_mail(
        subject="Unlock Your Account",
        message=f"Your account is locked due to multiple failed login attempts.\nClick the link below to unlock it:\n\n{unlock_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )




# Initialize Redis connection
redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True)

TOKEN_EXPIRY_SECONDS = 60 * 60 * 24  # 1 day

def store_active_token(user_id, token):
    """Store an active token in Redis with expiration."""
    redis_client.setex(f"active_token:{user_id}:{token}", TOKEN_EXPIRY_SECONDS, "valid")

def revoke_token(user_id, token):
    """Revoke a token in Redis."""
    redis_client.delete(f"active_token:{user_id}:{token}")

def is_token_revoked(user_id, token):
    """Check if a token is revoked."""
    return redis_client.get(f"active_token:{user_id}:{token}") is None

def send_mfa_email(user, subject, message):
    """
    Sends an MFA-related email notification to the user.
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

def notify_mfa_enabled(user):
    """
    Notify user when MFA is enabled.
    """
    subject = "Multi-Factor Authentication Enabled"
    message = f"Hello {user.username},\n\nMFA has been successfully enabled on your account."
    send_mfa_email(user, subject, message)

def notify_mfa_disabled(user):
    """
    Notify user when MFA is disabled.
    """
    subject = "Multi-Factor Authentication Disabled"
    message = f"Hello {user.username},\n\nMFA has been disabled on your account. If you did not request this, please secure your account immediately."
    send_mfa_email(user, subject, message)

def notify_mfa_reset(user):
    """
    Notify user when MFA is reset by an admin.
    """
    subject = "Multi-Factor Authentication Reset"
    message = f"Hello {user.username},\n\nYour MFA has been reset by an administrator. You need to set up MFA again."
    send_mfa_email(user, subject, message)

def send_mfa_recovery_email(user):
    """
    Sends an MFA recovery email with a secure link.
    """
    recovery_link = f"https://{user.website.domain}/mfa-recover/{user.mfa_recovery_token}"
    subject = "Multi-Factor Authentication Recovery"
    message = f"Hello {user.username},\n\nClick the link below to reset your MFA setup:\n\n{recovery_link}\n\nThis link expires in 15 minutes."
    
    send_mfa_email(user, subject, message)


def log_audit_action(user, action, request):
    """
    Logs an MFA-related action in the audit log.
    """
    from .models import AuditLog
    AuditLog.objects.create(
        user=user,
        action=action,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )


def require_mfa_verification(user, otp_code):
    """
    Checks if MFA is enabled and verifies the OTP code.
    """
    if user.is_mfa_enabled:
        if not otp_code:
            raise PermissionDenied("MFA verification required.")

        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(otp_code):
            raise PermissionDenied("Invalid MFA code.")


def send_security_alert(user, request):
    """Sends an email if a login occurs from an unrecognized IP or device."""
    ip_address = get_client_ip(request)
    device_info = get_device_info(request)
    send_mail(
        "Unusual Login Attempt Detected",
        f"A login was detected from {device_info} (IP: {ip_address}). If this wasn't you, reset your password immediately.",
        "no-reply@yourdomain.com",
        [user.email]
    )

def get_device_info(request):
    ua_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(ua_string)
    
    return {
        "browser": user_agent.browser.family,
        "os": user_agent.os.family,
        "device": user_agent.device.family,
        "is_mobile": user_agent.is_mobile,
        "is_tablet": user_agent.is_tablet,
        "is_pc": user_agent.is_pc,
    }


