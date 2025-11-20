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
    from authentication.models import AuditLog
    if not user or not action_type or not request:
        logger.error("Invalid parameters for logging audit action.")
        return
    if not isinstance(user, int):
        logger.error("User must be an instance of User model.")
        return
    if not isinstance(action_type, str):
        logger.error("Action type must be a string.")
        return
    if not isinstance(request, object):
        logger.error("Request must be an instance of HttpRequest.")
        return
    if reason is None:
        reason = "No specific reason provided"
    if not isinstance(reason, str):
        logger.error("Reason must be a string.")
        return
    # Extract IP address and user agent from the request
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