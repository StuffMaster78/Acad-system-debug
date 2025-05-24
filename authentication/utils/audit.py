from authentication.models.audit import AuditLog
from ipware import get_client_ip as ipware_get_ip # type: ignore
import logging

logger = logging.getLogger(__name__)

def log_audit_action(user, action_type, request, reason=None):
    """
    Log the user action (e.g., login, logout) for auditing purposes.
    
    Args:
        user: The user performing the action.
        action_type: The type of action being performed (e.g., "login", "logout").
        request: The HTTP request object to capture IP and user agent details.
        reason: An optional reason for the action, if applicable.
    """
    ip, _ = ipware_get_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")


    logger.info(
    f"User {user.id} performed action: {action_type} from IP {ip} "
    f"using agent {user_agent}. Reason: {reason}"
    )


    AuditLog.objects.create(
        user=user,
        action_type=action_type,
        ip_address=ip,
        session_key=request.session.session_key,
        user_agent=user_agent,
        path=request.get_full_path(),
        reason=reason
    )


def get_client_ip(request):
    """
    Extract the real client IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip